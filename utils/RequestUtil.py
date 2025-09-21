import json
import asyncio
import aiohttp

from astrbot.api import logger
from typing import Optional



GAMETOOLS_API_SITE = "https://api.gametools.network/"
BTR_API_SITE = "http://154.9.228.60:8766/api/"
SUPPORTED_GAMES = ["bf4","bf1", "bfv"]


async def gl_request_api(game, prop="stats", params=None, timeout=15, session=None):
    """
    异步请求API
        Args:
        game: 游戏代号(bfv/bf1/bf4)
        prop: 请求属性(stats/servers等)
        params: 查询参数
        timeout: 超时时间(秒)
        session: 可选的aiohttp.ClientSession实例
    Returns:
        JSON响应数据
    Raises:
        aiohttp.ClientError: 网络或HTTP错误
        json.JSONDecodeError: 响应不是合法JSON
    """
    if params is None:
        params = {}
    url = GAMETOOLS_API_SITE + f"{game}/{prop}"
    logger.info(f"Battlefield Tool Request Gametools API: {url}，请求参数: {params}")

    should_close = session is None
    if should_close:
        session = aiohttp.ClientSession()

    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.get(url, params=params, timeout=timeout_obj) as response:
            if response.status == 200:
                result = await response.json()
                result["code"] = response.status
                return result
            else:
                # 携带状态码和错误信息抛出
                error_dict = await response.json()
                error_dict["code"] = response.status
                error_msg = (
                    f"玩家 '{ea_name}' 未找到或游戏代号错误\n"
                    f"• 确认ID: {ea_name}\n"
                    f"• 游戏代号: {game}\n"
                    f"• 可用代号: {', '.join(SUPPORTED_GAMES)}"
                    f"• 原始错误: {error_dict}"
                )
                logger.error(f"Battlefield Tool 调用接口失败，错误信息{error_dict}")
                return error_msg
    except aiohttp.ClientError as e:
        error_msg = f"网络请求异常: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
    except json.JSONDecodeError as e:
        error_msg = f"JSON解析失败: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except asyncio.TimeoutError as e:
        error_msg = f"请求超时: {timeout}秒内未收到响应"
        logger.error(error_msg)
        raise TimeoutError(error_msg) from e
    finally:
        if should_close and session is not None:
            await session.close()


async def check_image_url_status(url: str) -> Optional[int]:
    """
    异步检查图片URL状态码

    Args:
        url: 要检查的图片URL

    Returns:
        状态码(成功时)或None(失败时)
    """
    timeout = aiohttp.ClientTimeout(total=5)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                return response.status
    except aiohttp.ClientError as e:
        logger.error(f"请求图片URL时发生错误: {e}")
        return None


async def btr_request_api(prop: str, params: Optional[dict] = None, timeout: int = 15, session: Optional[aiohttp.ClientSession] = None):
    """
    异步请求BTR API
        Args:
        prop: 请求属性
        params: 查询参数
        timeout: 超时时间(秒)
        session: 可选的aiohttp.ClientSession实例
    Returns:
        JSON响应数据
    Raises:
        aiohttp.ClientError: 网络或HTTP错误
        json.JSONDecodeError: 响应不是合法JSON
    """
    if params is None:
        params = {}
    url = BTR_API_SITE + prop
    logger.info(f"Battlefield Tool Request BTR API: {url}，请求参数: {params}")

    should_close = session is None
    if should_close:
        session = aiohttp.ClientSession()

    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.get(url, params=params, timeout=timeout_obj) as response:
            if response.status == 200:
                result = await response.json()
                result["code"] = response.status
                return result
            else:
                error_dict = await response.json()
                error_dict["code"] = response.status
                error_msg = (
                    f"Battlefield Tool 调用BTR接口失败，状态码: {response.status}, 错误信息: {error_dict}"
                )
                logger.error(error_msg)
                return error_dict
    except aiohttp.ClientError as e:
        error_msg = f"BTR API网络请求异常: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
    except json.JSONDecodeError as e:
        error_msg = f"BTR API JSON解析失败: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    except asyncio.TimeoutError as e:
        error_msg = f"BTR API请求超时: {timeout}秒内未收到响应"
        logger.error(error_msg)
        raise TimeoutError(error_msg) from e
    finally:
        if should_close and session is not None:
            await session.close()
