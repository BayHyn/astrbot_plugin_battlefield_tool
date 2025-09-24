from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from astrbot.api import logger
from constants.battlefield_constants import (
    ImageUrls, BackgroundColors, GameMappings, TemplateConstants
)

import time

# 获取模板
templates = TemplateConstants.get_templates()
MAIN_TEMPLATE = templates["main"]
WEAPONS_TEMPLATE = templates["weapons"]
VEHICLES_TEMPLATE = templates["vehicles"]
SERVERS_TEMPLATE = templates["servers"]
WEAPON_CARD = templates["weapon_card"]
VEHICLE_CARD = templates["vehicle_card"]
SERVER_CARD = templates["server_card"]


def sort_list_of_dicts(list_of_dicts, key):
    """降序排序"""
    return sorted(list_of_dicts, key=lambda k: k[key], reverse=True)


def prepare_weapons_data(d: dict, lens: int,game:str):
    """提取武器数据，格式化使用时间"""
    weapons_list = d["weapons"]
    weapons_list = sort_list_of_dicts(weapons_list, "kills")
    if game == "bf4":
        return [
            {**w, "__timeEquippedHours": 0, "timeEquipped": 0}
            for w in weapons_list[:lens]
            if  w.get("kills", 0) > 0
        ]
    else:
        return [
            {**w, "__timeEquippedHours": round(w.get("timeEquipped", 0) / 3600, 1)}
            for w in weapons_list[:lens]
            if  w.get("kills", 0) > 0
        ]

def prepare_vehicles_data(d: dict, lens: int):
    """提取载具数据，格式化使用时间"""
    vehicles_list = d["vehicles"]
    vehicles_list = sort_list_of_dicts(vehicles_list, "kills")
    return [
        {
            **w,
            "__timeInHour": round(w.get("timeIn", 0) / 3600, 1),
            "image": img_repair_vehicles(w.get("vehicleName", "").lower(),w.get("image", ""))
        }
        for w in vehicles_list[:lens]
        if  w.get("kills", 0) > 0
    ]

def img_repair_vehicles(item_name:str,url:str):
    """处理问题图片"""
    for item in ImageUrls.ERROR_IMG:
        if item["name"] == item_name:
            return item["repair_url"]
    return url



def bf_main_html_builder(d, game):
    """
    构建主要html
    Args:
        d: 查询到的数据
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER) # 使用.get()方法，提供默认值
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR) # 获取背景色
    if d.get("avatar") is None:
        d["avatar"] = ImageUrls.DEFAULT_AVATAR
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d["__update_time"]))
    d["__hoursPlayed"] = round(d["secondsPlayed"] / 3600, 1)
    d["revives"] = int(d["revives"])
    d["longestHeadShot"] = int(d["longestHeadShot"])

    # 整理数据
    weapon_data = prepare_weapons_data(d, 3,game)
    vehicle_data = prepare_vehicles_data(d, 3)

    html = MAIN_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=d,
        weapon_data=weapon_data if weapon_data else None,
        vehicle_data=vehicle_data if vehicle_data else None,
        game=game,
        background_color=background_color, # 传递背景色
    )
    return html


def bf_weapons_html_builder(d, game):
    """
    构建武器html
    Args:
        d: 查询到的数据
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR)
    if d.get("avatar") is None:
        d["avatar"] = ImageUrls.DEFAULT_AVATAR
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d["__update_time"]))

    # 整理数据
    weapon_data = prepare_weapons_data(d, 50,game)

    html = WEAPONS_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=d,
        weapon_data=weapon_data if weapon_data else None,
        game=game,
        background_color=background_color,
    )
    return html


def bf_vehicles_html_builder(d, game):
    """
    构建主要html
    Args:
        d: 查询到的数据
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR)
    if d.get("avatar") is None:
        d["avatar"] = ImageUrls.DEFAULT_AVATAR
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d["__update_time"]))

    # 整理数据
    vehicle_data = prepare_vehicles_data(d, 50)

    html = VEHICLES_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=d,
        vehicle_data=vehicle_data if vehicle_data else None,
        game=game,
        background_color=background_color,
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
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    logo = GameMappings.LOGOS.get(game, ImageUrls.BF3_LOGO)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR)
    update_time = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(servers_data["__update_time"])
    )

    html = SERVERS_TEMPLATE.render(
        banner=banner,
        logo=logo,
        update_time=update_time,
        servers_data=servers_data["servers"] if servers_data else None,
        game=game,
        background_color=background_color,
    )
    return html
