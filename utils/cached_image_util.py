from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from astrbot.api import logger
import time
import aiohttp
from functools import lru_cache

@lru_cache(maxsize=32)
async def get_cached_image(session: aiohttp.ClientSession, url: str) -> str:
    """异步获取并缓存图片内容，返回Base64 data URL"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            content = await response.read()
            mime_type = response.headers.get('Content-Type', 'image/png')
            base64_data = base64.b64encode(content).decode('utf-8')
            return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        logger.error(f"Failed to fetch image {url}: {e}")
        return None