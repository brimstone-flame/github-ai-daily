"""
配置管理模块
PushPlus Token 通过环境变量 PUSHPLUS_TOKEN 注入，
本地开发时可创建 .env 文件或直接设置环境变量。
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta


@dataclass
class Config:
    """应用配置"""

    # PushPlus
    pushplus_token: str = field(
        default_factory=lambda: os.environ.get("PUSHPLUS_TOKEN", "")
    )
    pushplus_api_url: str = "https://www.pushplus.plus/send"

    # 北京时区 (UTC+8)
    tz: timezone = field(default_factory=lambda: timezone(timedelta(hours=8)))

    # GitHub Trending
    github_trending_url: str = "https://github.com/trending"
    github_trending_count: int = 10

    # AI 新闻来源
    ai_news_sources: list[dict] = field(default_factory=lambda: [
        {
            "name": "IT之家",
            "url": "https://www.ithome.com/rss",
            "type": "rss",
        },
        {
            "name": "量子位",
            "url": "https://www.qbitai.com",
            "type": "web",
        },
        {
            "name": "TechCrunch AI",
            "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
            "type": "rss",
        },
        {
            "name": "The Verge AI",
            "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            "type": "rss",
        },
    ])
    # 每个来源最多获取的新闻条数
    max_news_per_source: int = 6

    @property
    def today_str(self) -> str:
        """返回北京时间的当日日期字符串"""
        return datetime.now(self.tz).strftime("%Y-%m-%d")

    @property
    def today_display(self) -> str:
        """返回用于显示的日期字符串，如 '2026年6月5日'"""
        now = datetime.now(self.tz)
        return f"{now.year}年{now.month}月{now.day}日"

    @property
    def now_time(self) -> str:
        """返回当前北京时间字符串"""
        return datetime.now(self.tz).strftime("%Y-%m-%d %H:%M")


# 全局单例
config = Config()
