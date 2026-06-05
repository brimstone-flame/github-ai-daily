"""
抓取 AI 行业新闻，支持多个来源（RSS 和 Web）。
每个来源独立抓取，单源失败不影响其他。
"""

import logging
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from lxml import etree

from src.config import config

logger = logging.getLogger(__name__)

# ── 请求头 ──────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass
class NewsItem:
    """单条 AI 新闻"""

    title: str
    url: str
    summary: str
    source: str  # 来源名称，如 "机器之心"


# ── 公共入口 ──────────────────────────────────────────

def fetch_all_news(sources: list[dict] | None = None) -> list[NewsItem]:
    """
    从所有配置的来源抓取 AI 新闻。

    Args:
        sources: 新闻来源列表，默认使用 config 中的配置。
                 每个来源 dict 包含 name, url, type(rss/web)。

    Returns:
        NewsItem 列表，已去重。
    """
    if sources is None:
        sources = config.ai_news_sources

    all_items: list[NewsItem] = []

    for src in sources:
        name = src.get("name", "Unknown")
        url = src.get("url", "")
        src_type = src.get("type", "rss")

        logger.info("正在抓取 %s (%s)", name, url)
        try:
            if src_type == "rss":
                items = _fetch_rss(name, url)
            else:
                items = _fetch_web(name, url)

            logger.info("%s: 获取到 %d 条新闻", name, len(items))
            all_items.extend(items)
        except Exception:
            logger.exception("%s: 抓取失败，已跳过", name)
            all_items.append(
                NewsItem(
                    title=f"[{name} 获取失败，请稍后重试]",
                    url="",
                    summary="",
                    source=name,
                )
            )

    # 去重：按标题相似度
    deduped = _deduplicate(all_items)
    logger.info(
        "总计 %d 条新闻，去重后 %d 条", len(all_items), len(deduped)
    )
    return deduped


# ── RSS 抓取 ──────────────────────────────────────────

def _fetch_rss(source_name: str, url: str) -> list[NewsItem]:
    """抓取 RSS / Atom feed，返回新闻列表；若返回 HTML 则降级为网页抓取"""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    # 内容类型检测：HTML 页面降级为网页抓取
    content_type = resp.headers.get("Content-Type", "").lower()
    if "text/html" in content_type:
        logger.info("%s: RSS 端点返回 HTML，降级为网页抓取", source_name)
        return _fetch_web(source_name, url)

    # 手动检测：以 '<!DOCTYPE' 或 '<html' 开头的是 HTML 页面
    text_start = resp.text[:200].strip().lower()
    if text_start.startswith("<!doctype") or text_start.startswith("<html"):
        logger.info("%s: 响应内容为 HTML，降级为网页抓取", source_name)
        return _fetch_web(source_name, url)

    # 使用正确的编码解析 XML
    if resp.encoding and resp.encoding.lower() != "utf-8":
        resp.encoding = "utf-8"

    # 用 lxml 解析 XML
    try:
        root = etree.fromstring(resp.content)
    except etree.XMLSyntaxError:
        # BeautifulSoup 清理后取 bytes（避免 str 带 XML declaration 的问题）
        try:
            soup = BeautifulSoup(resp.content, "xml")
            root = etree.fromstring(soup.encode())
        except (etree.XMLSyntaxError, ValueError):
            logger.warning("%s: XML 解析失败，降级为网页抓取", source_name)
            return _fetch_web(source_name, url)

    items: list[NewsItem] = []

    # 尝试 Atom 格式: /feed/entry
    nsmap = _get_nsmap(root)
    entries = root.findall(".//entry", nsmap) or root.findall(".//{http://www.w3.org/2005/Atom}entry")
    if entries:
        for entry in entries[:config.max_news_per_source]:
            title = _text(entry, "title", nsmap)
            link = _link(entry, nsmap)
            summary = _text(entry, "summary", nsmap) or _text(entry, "content", nsmap)
            summary = _clean_summary(summary)

            if title and link:
                items.append(NewsItem(title=title, url=link, summary=summary, source=source_name))
        return items

    # 尝试 RSS 2.0 格式: /rss/channel/item
    ns_items = root.findall(".//item", nsmap) or root.findall(".//{http://purl.org/rss/1.0/}item")
    if not ns_items:
        # 不带命名空间再试
        for elem in root.iter():
            if elem.tag.endswith("item") or elem.tag == "item":
                ns_items.append(elem)

    for item in ns_items[:config.max_news_per_source]:
        title = _text(item, "title", nsmap)
        link = _text(item, "link", nsmap) or _link(item, nsmap)
        summary = _text(item, "description", nsmap) or _text(item, "summary", nsmap)
        summary = _clean_summary(summary)

        if title and link:
            items.append(NewsItem(title=title, url=link, summary=summary, source=source_name))

    return items


def _get_nsmap(root) -> dict:
    """获取 XML 根元素的命名空间映射"""
    nsmap = {}
    if hasattr(root, "nsmap") and root.nsmap:
        nsmap = dict(root.nsmap)
    return nsmap


def _text(element, tag: str, nsmap: dict) -> str:
    """从元素中提取指定标签的文本，支持命名空间"""
    # Atom 命名空间
    atom_ns = "http://www.w3.org/2005/Atom"
    for ns in [None, atom_ns]:
        if ns:
            el = element.find(f"{{{ns}}}{tag}")
        else:
            el = element.find(tag, nsmap)
        if el is None and nsmap:
            el = element.find(tag, nsmap)
        if el is not None:
            return (el.text or "").strip()
    return ""


def _link(element, nsmap: dict) -> str:
    """从元素中提取链接，支持 Atom 和 RSS"""
    # Atom: <link href="..."/>
    atom_ns = "{http://www.w3.org/2005/Atom}"
    for link_el in element.findall(f"{atom_ns}link"):
        href = link_el.get("href", "")
        if href:
            return href.strip()

    # 通用 link 子元素
    link_el = element.find("link", nsmap)
    if link_el is not None:
        # Atom link 可能是空元素带 href 属性
        href = link_el.get("href", "")
        if href:
            return href.strip()
        return (link_el.text or "").strip()

    return ""


# ── Web 抓取（量子位等）───────────────────────────────

def _fetch_web(source_name: str, url: str) -> list[NewsItem]:
    """通用网页抓取，尝试从常见文章列表中提取新闻"""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    if resp.encoding and resp.encoding.lower() != "utf-8":
        resp.encoding = "utf-8"

    soup = BeautifulSoup(resp.text, "lxml")
    items: list[NewsItem] = []

    # 策略 1: 查找 <article> 标签
    articles = soup.find_all("article")
    if articles:
        for art in articles[:config.max_news_per_source]:
            item = _parse_article_element(art, source_name, url)
            if item:
                items.append(item)
        if items:
            return items

    # 策略 2: 查找常见列表容器
    selectors = [
        "div.article-item", "div.post-item", "li.news-item",
        "div.news-list > div", "div[class*='article']",
        "div[class*='post']", "li[class*='news']",
    ]
    for sel in selectors:
        candidates = soup.select(sel)
        if candidates:
            for c in candidates[:config.max_news_per_source]:
                item = _parse_article_element(c, source_name, url)
                if item:
                    items.append(item)
            if items:
                return items

    # 策略 3: 查找任何带标题的链接
    for a_tag in soup.find_all("a", href=True):
        text = a_tag.get_text(strip=True)
        if len(text) > 15:  # 足够长的文本才可能是新闻标题
            href = a_tag["href"]
            full_url = urljoin(url, href)
            items.append(NewsItem(title=text, url=full_url, summary="", source=source_name))
        if len(items) >= config.max_news_per_source:
            break

    return items


def _parse_article_element(element, source_name: str, base_url: str) -> NewsItem | None:
    """从 article / div 元素中提取标题和链接"""
    # 查找标题链接
    title_tag = element.find(["h1", "h2", "h3", "h4", "a"])
    if not title_tag:
        return None

    # 如果标题标签不是 a，则在其内部找 a
    a_tag = title_tag if title_tag.name == "a" else title_tag.find("a")
    if not a_tag:
        return None

    title = a_tag.get_text(strip=True)
    href = a_tag.get("href", "")
    if not title or not href:
        return None

    full_url = urljoin(base_url, href)

    # 尝试获取摘要
    summary = ""
    p_tag = element.find("p")
    if p_tag:
        summary = p_tag.get_text(strip=True)
        if len(summary) > 200:
            summary = summary[:197] + "..."

    return NewsItem(title=title, url=full_url, summary=summary, source=source_name)


# ── 公共工具 ──────────────────────────────────────────

def _clean_summary(text: str) -> str:
    """清理摘要文本：去 HTML 标签，截断"""
    if not text:
        return ""
    # 去掉 HTML 标签
    clean = re.sub(r"<[^>]+>", "", text)
    # 合并空白
    clean = re.sub(r"\s+", " ", clean).strip()
    # 截断
    if len(clean) > 200:
        clean = clean[:197] + "..."
    return clean


def _title_similarity(a: str, b: str) -> float:
    """计算两个标题的相似度 (0.0 ~ 1.0)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _deduplicate(items: list[NewsItem], threshold: float = 0.75) -> list[NewsItem]:
    """
    基于标题相似度去重。保留先出现的条目。
    失败占位条目（url 为空）始终保留不去重。
    """
    kept: list[NewsItem] = []
    for item in items:
        # 保留失败占位
        if not item.url:
            kept.append(item)
            continue
        # 检查是否与已保留的条目相似
        is_dup = False
        for k in kept:
            if not k.url:
                continue
            if _title_similarity(item.title, k.title) >= threshold:
                is_dup = True
                break
            # 同一 URL 直接视为重复
            if item.url == k.url:
                is_dup = True
                break
        if not is_dup:
            kept.append(item)
    return kept
