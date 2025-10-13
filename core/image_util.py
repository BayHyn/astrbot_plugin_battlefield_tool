import base64
import os
from typing import Optional
from urllib.parse import urlparse
from astrbot.api import logger
from astrbot.api.star import StarTools
import mimetypes # 导入 mimetypes 模块

from .request_util import fetch_image

image_dir = StarTools.get_data_dir("battleField_tool_plugin/images")
image_dir.mkdir(parents=True, exist_ok=True)


def _get_mime_type(file_path: str) -> str:
    """
    根据文件路径获取MIME类型。
    Args:
        file_path: 文件路径。
    Returns:
        文件的MIME类型，如果无法确定则返回'application/octet-stream'。
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type if mime_type else 'application/octet-stream'


def get_local_image_path(image_url: str) -> str:
    """
    根据图片URL生成本地存储路径。
    Args:
        image_url: 图片的URL。
    Returns:
        本地图片文件的完整路径。
    """
    parsed_url = urlparse(image_url)
    file_name = os.path.basename(parsed_url.path)
    return os.path.join(image_dir, file_name)


def image_to_base64(image_path: str) -> Optional[str]:
    """
    将本地图片文件转换为HTML可用的Base64编码字符串。

    Args:
        image_path: 图片文件的路径。

    Returns:
        图片的HTML可用的Base64编码字符串（data:image/<format>;base64,...），
        如果文件不存在或读取失败则返回None。
    """
    if not os.path.exists(image_path):
        logger.debug(f"图片文件未找到: {image_path}")
        return None
    
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        mime_type = _get_mime_type(image_path)
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        logger.error(f"读取或编码图片文件失败: {e}")
        return None


def svg_to_base64(svg_path: str) -> Optional[str]:
    """
    将本地SVG文件转换为HTML可用的Base64编码字符串。

    Args:
        svg_path: SVG文件的路径。

    Returns:
        SVG的HTML可用的Base64编码字符串（data:image/svg+xml;base64,...），
        如果文件不存在或读取失败则返回None。
    """
    if not os.path.exists(svg_path):
        logger.debug(f"SVG文件未找到: {svg_path}")
        return None
    
    try:
        with open(svg_path, "r", encoding="utf-8") as svg_file:
            svg_content = svg_file.read()
            encoded_string = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
        # SVG的MIME类型通常是 image/svg+xml
        return f"data:image/svg+xml;base64,{encoded_string}"
    except Exception as e:
        logger.error(f"读取或编码SVG文件失败: {e}")
        return None


def save_image_to_local(image_path: str, image_data: bytes):
    """
    将二进制图片数据保存到本地文件。
    Args:
        image_path: 本地图片文件的完整路径。
        image_data: 图片的二进制数据。
    """
    try:
        with open(image_path, "wb") as f:
            f.write(image_data)
        logger.debug(f"图片已保存到本地: {image_path}")
    except Exception as e:
        logger.error(f"保存图片到本地失败: {e}")


async def get_image_base64(image_url: str, timeout: int = 15) -> Optional[str]:
    """
    先尝试从本地获取图片并转换为HTML可用的Base64编码。
    如果本地不存在，则从远程URL获取图片，保存到本地，然后返回HTML可用的Base64编码。
    Args:
        image_url: 图片的URL。
        timeout: 远程请求的超时时间(秒)。
    Returns:
        图片的HTML可用的Base64编码字符串（data:image/<format>;base64,...），
        如果获取失败则返回None。
    """
    local_path = get_local_image_path(image_url)
    
    # 尝试从本地获取
    base64_data = None
    if local_path.lower().endswith(".svg"):
        base64_data = svg_to_base64(local_path)
    else:
        base64_data = image_to_base64(local_path)

    if base64_data:
        logger.debug(f"图片已从本地获取并转换为Base64: {local_path}")
        return base64_data
    
    logger.debug(f"本地未找到图片，尝试从远程获取: {image_url}")
    # 本地不存在，从远程获取
    image_data = await fetch_image(image_url, timeout)
    if image_data:
        # 保存到本地
        save_image_to_local(local_path, image_data)
        # 再次从本地读取并转换为Base64
        if local_path.lower().endswith(".svg"):
            base64_data = svg_to_base64(local_path)
        else:
            base64_data = image_to_base64(local_path)

        if base64_data:
            logger.debug(f"图片已从远程获取、保存到本地并转换为Base64: {local_path}")
            return base64_data
    
    logger.error(f"无法获取图片并转换为Base64: {image_url}")
    return None
