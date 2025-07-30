from functools import lru_cache
from astrbot.api import logger
from typing import Dict, Optional
from ..constants.image_urls import ImageUrls

import base64
import aiohttp
import asyncio

class ImageCacheManager:
    """图片缓存管理器"""
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._preloaded_images: Dict[str, str] = {}  # 静态预加载图片
        self._dynamic_cache: Dict[str, str] = {}  # 动态图片缓存

    async def initialize(self):
        """初始化缓存管理器"""
        self._session = aiohttp.ClientSession()

    async def close(self):
        """关闭资源"""
        if self._session:
            await self._session.close()

    async def _fetch_and_encode_image(self, url: str, retry: int = 3) -> Optional[str]:
        """优化版图片下载方法，添加浏览器级优化和CDN适配
        Args:
            url: 图片URL (支持自动处理EA CDN)
            retry: 重试次数 (默认3次，使用指数退避)
        """
        if not self._session:
            raise RuntimeError("ImageCacheManager not initialized")

        # 浏览器级请求头优化
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.battlefield.com/"
        }

        last_error = None
        for attempt in range(1, retry + 1):
            try:
                # 尝试多个CDN端点
                effective_url = self._optimize_cdn_url(url) if "akamaihd.net" in url else url

                async with self._session.get(
                        effective_url,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=15),
                        compress=True,
                        allow_redirects=True
                ) as response:
                    if response.status == 404:
                        return None  # 明确处理404情况

                    response.raise_for_status()

                    # 流式读取优化大文件
                    content = bytearray()
                    async for chunk in response.content.iter_chunked(8192):
                        content.extend(chunk)

                    mime_type = response.headers.get('Content-Type', 'image/png')
                    base64_data = base64.b64encode(content).decode('utf-8')
                    return f"data:{mime_type};base64,{base64_data}"

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = e
                logger.warning(f"Attempt {attempt}/{retry} failed for {url}: {type(e).__name__}")
                if attempt < retry:
                    await asyncio.sleep(min(2 ** attempt, 5))  # 上限5秒的指数退避
                continue

        logger.error(f"Failed after {retry} attempts for {url}: {str(last_error)}")
        return None
    def _optimize_cdn_url(self, original_url: str) -> str:
        """优化EA CDN URL"""
        cdn_endpoints = [
            "eaassets-a.akamaihd.net",
            "eaassets-a.conduit.akamaihd.net",
            "eaassets.akamaized.net"
        ]

        if any(endpoint in original_url for endpoint in cdn_endpoints):
            return original_url

        # 自动选择最快CDN (简单实现，实际可添加CDN测速逻辑)
        return original_url.replace(
            "eaassets-a.akamaihd.net",
            cdn_endpoints[0]  # 默认第一个，可扩展智能选择
        )

    @lru_cache(maxsize=32)
    async def get_image(self, url: str) -> Optional[str]:
        """获取并缓存图片内容，返回Base64 data URL"""
        return await self._fetch_and_encode_image(url)

    async def preload_images(self, image_map: Dict[str, str]):
        """预加载常用图片"""
        for name, url in image_map.items():
            self._preloaded_images[name] = await self._fetch_and_encode_image(url)

    def get_preloaded(self, name: str) -> Optional[str]:
        """获取预加载的图片"""
        return self._preloaded_images.get(name)

    async def get_or_set_image(self, key: str, url: str, retry: int = 3) -> Optional[str]:
        """获取或设置图片缓存
        Args:
            key: 缓存键名
            url: 图片URL
            retry: 重试次数，默认为3次
        """
        if key in self._dynamic_cache:
            return self._dynamic_cache[key]

        image_data = await self._fetch_and_encode_image(url, retry)
        if image_data:
            self._dynamic_cache[key] = image_data
        return image_data

    async def get_with_fallback(self, key: str, url: str, fallback_key: str) -> str:
        """获取图片，失败时返回备用图片
        Args:
            key: 主图片缓存键
            url: 主图片URL
            fallback_key: 备用图片键名
        Returns:
            返回Base64编码的图片数据
        """
        result = await self.get_or_set_image(key, url)
        if result is None and fallback_key:
            result = self.get_preloaded(fallback_key)
            if result is None:
                logger.error(f"Both primary and fallback images unavailable (key: {key}, fallback: {fallback_key})")
        return result or ""

# 全局缓存实例
image_cache = ImageCacheManager()

async def init_image_cache(background_load: bool = True):
    """初始化图片缓存
    Args:
        background_load: 是否在后台异步加载图片
    """
    await image_cache.initialize()

    if background_load:
        # 创建后台任务不阻塞主流程
        asyncio.create_task(_background_preload_images())
    else:
        await _background_preload_images()

async def _background_preload_images():
    """后台预加载图片"""
    logger.info("Battlefield_tool starting background image preloading...")
    try:
        urls = ImageUrls.get_all_static_urls()
        # 分批加载避免瞬时IO压力
        batch_size = 5
        for i in range(0, len(urls), batch_size):
            batch = dict(list(urls.items())[i:i + batch_size])
            await image_cache.preload_images(batch)
        logger.info("Battlefield_tool image preloading completed")
    except Exception as e:
        logger.error(f"Battlefield_tool background preload failed: {e}")