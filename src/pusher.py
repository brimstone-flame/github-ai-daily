"""
PushPlus 推送模块
通过 PushPlus API 将消息推送到个人微信。
API 文档: https://www.pushplus.plus/doc/
"""

import logging

import requests

from src.config import config

logger = logging.getLogger(__name__)


def push_message(
    content: str,
    title: str | None = None,
    template: str = "markdown",
) -> bool:
    """
    通过 PushPlus 推送消息到微信。

    Args:
        content: 消息正文（Markdown 格式）
        title: 消息标题，默认使用当日日期
        template: 消息模板类型，支持 "html", "markdown", "txt"

    Returns:
        True 表示推送成功，False 表示失败
    """
    token = config.pushplus_token
    if not token:
        logger.error(
            "PUSHPLUS_TOKEN 未设置！"
            "请设置环境变量 PUSHPLUS_TOKEN 或在 GitHub Secrets 中配置。"
        )
        return False

    if title is None:
        title = f"GitHub & AI 日报 — {config.today_display}"

    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": template,
    }

    try:
        logger.info("正在通过 PushPlus 推送消息...")
        resp = requests.post(
            config.pushplus_api_url,
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()

        # PushPlus 返回码: 200 表示成功
        code = result.get("code", -1)
        if code == 200:
            logger.info("PushPlus 推送成功 ✓")
            return True
        else:
            msg = result.get("msg", "未知错误")
            logger.error("PushPlus 推送失败: code=%s, msg=%s", code, msg)
            return False

    except requests.RequestException as e:
        logger.error("PushPlus API 请求失败: %s", e)
        return False
    except ValueError as e:
        logger.error("PushPlus API 返回非 JSON 响应: %s", e)
        return False
