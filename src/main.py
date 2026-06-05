"""
主入口 — 编排每日推送流程

流程:
1. 抓取 GitHub Trending Top 10
2. 抓取 AI 行业新闻（多源）
3. 翻译英文内容为中文
4. 格式化为 Markdown 消息
5. 通过 PushPlus 推送到微信
"""

import logging
import sys

from src.config import config
from src.fetchers.github_trending import fetch_trending
from src.fetchers.ai_news import fetch_all_news, NewsItem
from src.formatter import format_message
from src.pusher import push_message
from src.translator import translate

# ── 日志配置 ──────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


# ── 翻译处理 ──────────────────────────────────────────

def _translate_news(items: list[NewsItem]) -> list[NewsItem]:
    """将英文新闻标题和摘要翻译为中文"""
    logger.info("正在翻译英文新闻...")
    translated = 0
    for item in items:
        # 翻译标题
        new_title = translate(item.title)
        if new_title != item.title:
            translated += 1
        # 翻译摘要
        new_summary = translate(item.summary) if item.summary else ""
        if new_summary != item.summary:
            translated += 1

        item.title = new_title
        item.summary = new_summary

    logger.info("翻译完成，共处理 %d 处英文内容", translated)
    return items


# ── 主流程 ────────────────────────────────────────────

def run() -> bool:
    """
    执行每日推送流程。

    Returns:
        True 表示所有步骤成功，False 表示部分失败。
    """
    logger.info("=" * 50)
    logger.info("GitHub & AI 日报推送 — %s", config.today_display)
    logger.info("=" * 50)

    # Step 1: 抓取 GitHub Trending
    logger.info("[1/5] 抓取 GitHub Trending...")
    repos = fetch_trending(
        url=config.github_trending_url,
        count=config.github_trending_count,
    )
    logger.info("获取到 %d 个 GitHub Trending 项目", len(repos))

    # Step 2: 抓取 AI 新闻
    logger.info("[2/5] 抓取 AI 新闻...")
    news_items = fetch_all_news()
    logger.info("获取到 %d 条 AI 新闻", len(news_items))

    # Step 3: 翻译英文内容
    logger.info("[3/5] 翻译英文内容...")
    news_items = _translate_news(news_items)

    # Step 4: 格式化消息
    logger.info("[4/5] 格式化消息...")
    message = format_message(repos, news_items)

    # Step 5: 推送
    logger.info("[5/5] 推送到微信...")
    success = push_message(message)

    # 最终汇总
    logger.info("=" * 50)
    if success:
        logger.info("✅ 推送完成！")
    else:
        logger.warning(
            "⚠️ 推送未成功，请检查 PUSHPLUS_TOKEN 配置和网络连接"
        )
    logger.info("=" * 50)

    return success


# ── 命令行入口 ──────────────────────────────────────────

if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
