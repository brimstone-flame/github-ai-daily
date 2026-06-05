"""
消息格式化模块
将 GitHub Trending 和 AI 新闻数据格式化为淡蓝色主题的 Markdown 消息。
"""

import logging
from datetime import datetime

from src.config import config
from src.fetchers.github_trending import TrendingRepo
from src.fetchers.ai_news import NewsItem

logger = logging.getLogger(__name__)

# ── Markdown 模板组件 ─────────────────────────────────


def _header() -> str:
    """日期头部"""
    weekday = datetime.now(config.tz).strftime("%A")
    weekday_cn = {
        "Monday": "星期一",
        "Tuesday": "星期二",
        "Wednesday": "星期三",
        "Thursday": "星期四",
        "Friday": "星期五",
        "Saturday": "星期六",
        "Sunday": "星期日",
    }.get(weekday, weekday)
    return f"📅 **{config.today_display} {weekday_cn}** · GitHub & AI 日报"


def _divider() -> str:
    """分隔线"""
    return "\n\n━━━━━━━━━━━━━━━━━━\n\n"


def _thin_divider() -> str:
    """细分隔线"""
    return "\n\n"


def _github_section(repos: list[TrendingRepo]) -> str:
    """GitHub Trending 板块"""
    # 淡蓝色主题用 🔷 emoji 体现
    lines = ["🔷 **GitHub Trending Top 10**", ""]

    if not repos:
        lines.append("> ⚠️ GitHub Trending 数据获取失败，请稍后重试")
        return "\n".join(lines)

    for i, repo in enumerate(repos, 1):
        # 序号 + 项目名
        lines.append(f"**{i}.** 📦 [{repo.full_name}]({repo.url})")

        # 元信息行：语言 + 今日星数
        meta_parts = []
        if repo.language:
            meta_parts.append(f"🔤 {repo.language}")
        if repo.stars_today:
            meta_parts.append(f"⭐ {repo.stars_today}")
        if meta_parts:
            lines.append(f"　　{' · '.join(meta_parts)}")

        # 描述
        if repo.description:
            lines.append(f"　　📝 {repo.description}")

        lines.append("")  # 空行分隔

    return "\n".join(lines).rstrip()


def _news_section(news_items: list[NewsItem]) -> str:
    """AI 新闻板块，按来源分组"""
    lines = ["🤖 **AI 行业新闻**", ""]

    if not news_items:
        lines.append("> ⚠️ AI 新闻数据获取失败，请稍后重试")
        return "\n".join(lines)

    # 按来源分组
    groups: dict[str, list[NewsItem]] = {}
    for item in news_items:
        groups.setdefault(item.source, []).append(item)

    for source, items in groups.items():
        lines.append(f"**【{source}】**")
        for item in items:
            if item.url:
                lines.append(f"• [{item.title}]({item.url})")
            else:
                lines.append(f"• {item.title}")
            if item.summary:
                lines.append(f"　　_{item.summary}_")
        lines.append("")

    return "\n".join(lines).rstrip()


def _footer() -> str:
    """页脚"""
    return f"🕐 更新时间：{config.now_time}"


# ── 主入口 ────────────────────────────────────────────


def format_message(
    repos: list[TrendingRepo],
    news_items: list[NewsItem],
) -> str:
    """
    将 GitHub Trending 和 AI 新闻格式化为 Markdown 消息。

    Args:
        repos: GitHub Trending 项目列表
        news_items: AI 新闻列表

    Returns:
        格式化的 Markdown 字符串
    """
    logger.info("正在格式化推送消息...")

    parts = [
        _header(),
        _divider(),
        _github_section(repos),
        _divider(),
        _news_section(news_items),
        _divider(),
        _footer(),
    ]

    message = "".join(parts)
    logger.info("消息格式化完成，共 %d 字符", len(message))
    return message
