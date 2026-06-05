"""
抓取 GitHub Trending 页面，提取 Top N 热门项目。
"""

import logging
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class TrendingRepo:
    """GitHub Trending 项目"""

    owner: str
    name: str
    description: str
    language: str
    stars_today: str
    url: str

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


def fetch_trending(url: str, count: int = 10) -> list[TrendingRepo]:
    """
    抓取 GitHub Trending 页面，返回 Top N 项目列表。

    Args:
        url: GitHub Trending 页面 URL
        count: 返回的项目数量

    Returns:
        TrendingRepo 列表，抓取失败返回空列表
    """
    repos: list[TrendingRepo] = []

    try:
        logger.info("正在抓取 GitHub Trending: %s", url)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("GitHub Trending 请求失败: %s", e)
        return repos

    soup = BeautifulSoup(resp.text, "lxml")

    # GitHub Trending 页面的每个仓库在 <article class="Box-row"> 中
    articles = soup.find_all("article", class_="Box-row")
    if not articles:
        logger.warning("未找到 GitHub Trending 项目 (class='Box-row')，尝试备用选择器")
        # 备用: 尝试查找所有包含 h2 的 article
        articles = soup.find_all("article")

    logger.info("找到 %d 个 Trending 项目", len(articles))

    for article in articles[:count]:
        try:
            repo = _parse_article(article)
            if repo:
                repos.append(repo)
        except Exception as e:
            logger.warning("解析单个项目时出错: %s", e)
            continue

    logger.info("成功解析 %d 个 Trending 项目", len(repos))
    return repos


def _parse_article(article) -> TrendingRepo | None:
    """解析单个 article 元素为 TrendingRepo"""
    # 解析仓库名和链接
    h2 = article.find("h2")
    if not h2:
        return None

    link = h2.find("a")
    if not link:
        return None

    href = link.get("href", "").strip()
    # href 格式: /owner/repo
    if href.startswith("/"):
        href = href[1:]
    parts = href.split("/")
    if len(parts) < 2:
        return None
    owner, name = parts[0], parts[1]

    url = f"https://github.com/{owner}/{name}"

    # 解析描述
    desc = ""
    desc_tag = article.find("p")
    if desc_tag:
        desc = desc_tag.get_text(strip=True)
        # 过滤掉过长的描述
        if len(desc) > 200:
            desc = desc[:197] + "..."

    # 解析语言和今日星数
    language = ""
    stars_today = ""

    # 语言通常在含有 itemprop="programmingLanguage" 的 span 中
    lang_span = article.find("span", itemprop="programmingLanguage")
    if lang_span:
        language = lang_span.get_text(strip=True)

    # 今日星数通常包含 "stars today" 文本
    for span in article.find_all("span"):
        text = span.get_text(strip=True)
        if "stars today" in text.lower():
            stars_today = text
            break
    # 备用：查找包含 "stars" 的文本
    if not stars_today:
        for el in article.find_all(["span", "a"]):
            text = el.get_text(strip=True)
            if "star" in text.lower():
                stars_today = text
                break

    return TrendingRepo(
        owner=owner,
        name=name,
        description=desc,
        language=language,
        stars_today=stars_today,
        url=url,
    )
