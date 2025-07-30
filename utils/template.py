from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from astrbot.api import logger
from data.plugins.astrbot_plugin_battlefield_tool.utils.cached_image_util import image_cache

import aiohttp
import time

PARENT_FOLDER = Path(__file__).parent.parent.resolve()

# 创建Jinja2环境并设置模板加载路径
template_dir = PARENT_FOLDER / "template"
env = Environment(loader=FileSystemLoader(template_dir))

MAIN_TEMPLATE = env.get_template("template.html")
WEAPONS_TEMPLATE = env.get_template("template_weapons.html")
VEHICLES_TEMPLATE = env.get_template("template_vehicles.html")
SERVERS_TEMPLATE = env.get_template("template_servers.html")
WEAPON_CARD = env.get_template("weapon_card.html")
VEHICLE_CARD = env.get_template("vehicle_card.html")
SERVER_CARD = env.get_template("server_card.html")


def sort_list_of_dicts(list_of_dicts, key):
    """降序排序"""
    return sorted(list_of_dicts, key=lambda k: k[key], reverse=True)


async def prepare_weapons_data(d: dict, lens: int, game: str):
    """
    提取武器数据并处理图片缓存（单次循环优化版）
    :param d: 原始数据
    :param lens: 返回的武器数量
    :param game: 游戏类型
    :return: 处理后的武器列表
    """
    weapons_list = sort_list_of_dicts(d["weapons"], "kills")
    result = []

    for w in weapons_list[:lens]:
        if w.get("kills", 0) <= 0:
            continue

        # 同步处理基础数据
        weapon_data = {
            **w,
            "__timeEquippedHours": (
                0 if game == "bf4"
                else round(w.get("timeEquipped", 0) / 3600, 2)
            )
        }

        # 异步处理图片缓存
        if w.get("image"):
            weapon_data["cached_image"] = await image_cache.get_or_set_image(
                f"weapon_{w['weaponName']}_{game}",
                w["image"]
            )

        result.append(weapon_data)

    return result

async def prepare_vehicles_data(d: dict, lens: int, game: str):
    """提取载具数据，格式化使用时间并处理图片缓存"""
    vehicles_list = d["vehicles"]
    vehicles_list = sort_list_of_dicts(vehicles_list, "kills")
    result = []

    for v in vehicles_list[:lens]:
        if v.get("kills", 0) <= 0:
            continue

        # 同步处理基础数据
        vehicle_data = {
            **v,
            "__timeInHour": round(v.get("timeIn", 0) / 3600, 2),
            "image": SU_50 if v.get("vehicleName", "").lower() == "su-50" else v.get("image", "")
        }

        # 异步处理图片缓存
        if v.get("image"):
            vehicle_data["cached_image"] = await image_cache.get_or_set_image(
                f"vehicle_{v['vehicleName']}_{game}",
                v["image"]
            )

        result.append(vehicle_data)

    return result


async def bf_main_html_builder(d, game):
    """
    构建主要html
    Args:
        d: 查询到的数据
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = image_cache.get_preloaded(f"{game}_banner")
    if d.get("avatar") is None:
        d["avatar"] = image_cache.get_preloaded("default_avatar")

    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d["__update_time"]))
    d["__hoursPlayed"] = round(d["secondsPlayed"] / 3600, 2)
    d["revives"] = int(d["revives"])
    d["longestHeadShot"] = int(d["longestHeadShot"])

    # 整理数据
    weapon_data = await prepare_weapons_data(d, 5,game)
    vehicle_data = await prepare_vehicles_data(d, 5,game)

    html = MAIN_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=d,
        weapon_data=weapon_data if weapon_data else None,
        vehicle_data=vehicle_data if vehicle_data else None,
        game=game,
    )
    return html


async def bf_weapons_html_builder(d, game):
    """
    构建武器html
    Args:
        d: 查询到的数据
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = image_cache.get_preloaded(f"{game}_banner")
    if d.get("avatar") is None:
        d["avatar"] = image_cache.get_preloaded("default_avatar")
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d["__update_time"]))

    # 整理数据
    weapon_data = await prepare_weapons_data(d, 50,game)

    html = WEAPONS_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=d,
        weapon_data=weapon_data if weapon_data else None,
        game=game,
    )
    return html


async def bf_vehicles_html_builder(d, game):
    """
    构建主要html
    Args:
        d: 查询到的数据
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = image_cache.get_preloaded(f"{game}_banner")
    if d.get("avatar") is None:
        d["avatar"] = image_cache.get_preloaded("default_avatar")
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d["__update_time"]))

    # 整理数据
    vehicle_data = await prepare_vehicles_data(d, 50,game)

    html = VEHICLES_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=d,
        vehicle_data=vehicle_data if vehicle_data else None,
        game=game,
    )
    return html


def bf_servers_html_builder(servers_data, game):
    """
    构建主要html
    Args:
        servers_data: 查询到的数据
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = image_cache.get_preloaded(f"{game}_banner")
    logo = image_cache.get_preloaded(f"{game}_logo")
    update_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(servers_data["__update_time"])
    )

    html = SERVERS_TEMPLATE.render(
        banner=banner,
        logo=logo,
        update_time=update_time,
        servers_data=servers_data["servers"] if servers_data else None,
        game=game,
    )
    return html
