"""
翻译工具模块
将英文标题/摘要翻译为中文，用于英文新闻源的本地化。
双后端策略：Google Translate (GitHub Actions 美国服务器) → MyMemory (国内可用回退)
"""

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

import requests
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# Google Translate 超时秒数（国内网络不通，快速失败回退 MyMemory）
GOOGLE_TIMEOUT = 5

# 单例
_translator: GoogleTranslator | None = None
_google_available: bool | None = None  # None=未检测, True=可用, False=不可用


def _get_google_translator() -> GoogleTranslator:
    """获取 Google 翻译器单例"""
    global _translator
    if _translator is None:
        _translator = GoogleTranslator(source="auto", target="zh-CN")
    return _translator


def _is_english(text: str) -> bool:
    """简单判断文本是否主要为英文（拉丁字母比例 > 70%）"""
    if not text:
        return False
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    total = sum(1 for c in text if c.isalpha())
    if total == 0:
        return False
    return latin / total > 0.7


def _translate_google(text: str) -> str | None:
    """Google Translate 翻译，带超时的快速失败"""
    def _do_translate():
        translator = _get_google_translator()
        return translator.translate(text[:500])

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_do_translate)
            result = future.result(timeout=GOOGLE_TIMEOUT)
            if result and result != text:
                return result
    except (FuturesTimeoutError, Exception):
        logger.debug("Google 翻译不可用，尝试回退方案")
    return None


def _translate_mymemory(text: str) -> str | None:
    """MyMemory 免费 API 翻译，失败返回 None"""
    try:
        resp = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text[:500], "langpair": "en|zh"},
            timeout=10,
        )
        data = resp.json()
        result = data.get("responseData", {}).get("translatedText", "")
        if result and result != text:
            return result
    except Exception:
        logger.debug("MyMemory 翻译不可用")
    return None


def translate(text: str) -> str:
    """
    将文本翻译为中文。非英文直接返回原文。
    优先 Google Translate（5s 超时），失败回退 MyMemory，均失败保留原文。
    Google 一旦失败则后续直接跳过。
    """
    global _google_available

    if not text or not _is_english(text):
        return text

    # 尝试 Google Translate（仅当之前未失败过）
    if _google_available is not False:
        result = _translate_google(text)
        if result:
            _google_available = True
            return result
        # 标记 Google 不可用，后续直接走 MyMemory
        _google_available = False

    # 回退 MyMemory（国内可用）
    result = _translate_mymemory(text)
    if result:
        return result

    logger.debug("翻译服务均不可用，保留原文")
    return text


def translate_batch(texts: list[str]) -> list[str]:
    """批量翻译"""
    return [translate(t) for t in texts]
