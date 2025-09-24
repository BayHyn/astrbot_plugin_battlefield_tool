from astrbot.api import logger
from constants.battlefield_constants import (ImageUrls, BackgroundColors, GameMappings, TemplateConstants)
from models.entities import PlayerStats, Weapon, Vehicle # 导入实体类
from typing import List

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


def prepare_weapons_data(d: dict, lens: int, game: str) -> List[Weapon]:
    """提取武器数据，格式化使用时间，并返回 Weapon 对象列表"""
    weapons_list_raw = d.get("weapons", [])
    weapons_list_raw = sort_list_of_dicts(weapons_list_raw, "kills")
    
    weapons_objects = []
    for w_data in weapons_list_raw[:lens]:
        if w_data.get("kills", 0) > 0:
            # 根据游戏类型处理 timeEquipped
            if game == "bf4":
                w_data["timeSpent"] = "0" # bf4 武器时间不显示，设为0
            
            # 计算 kpm 和 timeEquipped 并转换为 str 类型
            w_data["killsPerMinute"] = str(round(w_data.get("killsPerMinute", 0.0), 2))
            w_data["timeSpent"] = str(round(w_data.get("timeEquipped", 0.0) / 3600, 1)) # 转换为小时

            # 创建 Weapon 对象
            weapon = Weapon.from_dict(w_data)
            weapons_objects.append(weapon)
            
    return weapons_objects

def prepare_vehicles_data(d: dict, lens: int) -> List[Vehicle]:
    """提取载具数据，格式化使用时间，并返回 Vehicle 对象列表"""
    vehicles_list_raw = d.get("vehicles", [])
    vehicles_list_raw = sort_list_of_dicts(vehicles_list_raw, "kills")

    vehicles_objects = []
    for v_data in vehicles_list_raw[:lens]:
        if v_data.get("kills", 0) > 0:
            # 处理图片URL
            v_data["image"] = img_repair_vehicles(v_data.get("vehicleName", "").lower(), v_data.get("image", ""))
            
            # 计算 kpm 和 timeSpent 并转换为 str 类型
            v_data["killsPerMinute"] = str(round(v_data.get("killsPerMinute", 0.0), 2))
            v_data["timeSpent"] = str(round(v_data.get("timeIn", 0.0) / 3600, 1)) # 转换为小时

            # 创建 Vehicle 对象
            vehicle = Vehicle.from_dict(v_data)
            vehicles_objects.append(vehicle)
            
    return vehicles_objects

def img_repair_vehicles(item_name:str,url:str):
    """处理问题图片"""
    for item in ImageUrls.ERROR_IMG:
        if item["name"] == item_name:
            return item["repair_url"]
    return url



def bf_main_html_builder(raw_data: dict, game: str) -> str:
    """
    构建主要html
    Args:
        raw_data: 查询到的原始数据字典
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR)

    # 预处理原始数据，使其符合 PlayerStats.from_dict 的期望
    processed_data = raw_data.copy()
    if processed_data.get("avatar") is None:
        processed_data["avatar"] = ImageUrls.DEFAULT_AVATAR
    
    # 计算 hoursPlayed 并添加到 processed_data，以便 PlayerStats.from_dict 使用
    processed_data["__hoursPlayed"] = str(round(processed_data.get("secondsPlayed", 0) / 3600, 1))
    processed_data["revives"] = int(processed_data.get("revives", 0))
    processed_data["longestHeadShot"] = int(processed_data.get("longestHeadShot", 0))

    # 创建 PlayerStats 对象
    player_stats = PlayerStats.from_dict(processed_data)
    
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(raw_data["__update_time"]))

    # 整理武器和载具数据，返回实体对象列表
    weapons_objects = prepare_weapons_data(raw_data, 3, game)
    vehicles_objects = prepare_vehicles_data(raw_data, 3)

    # 将实体对象转换回字典，以便 Jinja2 模板渲染
    player_stats_dict = player_stats.to_dict()
    weapon_data_dicts = [w.to_dict() for w in weapons_objects] if weapons_objects else None
    vehicle_data_dicts = [v.to_dict() for v in vehicles_objects] if vehicles_objects else None

    html = MAIN_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=player_stats_dict, # 传递 PlayerStats 对象的字典表示
        weapon_data=weapon_data_dicts,
        vehicle_data=vehicle_data_dicts,
        game=game,
        background_color=background_color,
    )
    return html


def bf_weapons_html_builder(raw_data: dict, game: str) -> str:
    """
    构建武器html
    Args:
        raw_data: 查询到的原始数据字典
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR)

    # 预处理原始数据，使其符合 PlayerStats.from_dict 的期望
    processed_data = raw_data.copy()
    if processed_data.get("avatar") is None:
        processed_data["avatar"] = ImageUrls.DEFAULT_AVATAR
    
    # 计算 hoursPlayed 并添加到 processed_data，以便 PlayerStats.from_dict 使用
    processed_data["__hoursPlayed"] = str(round(processed_data.get("secondsPlayed", 0) / 3600, 1))
    processed_data["revives"] = int(processed_data.get("revives", 0))
    processed_data["longestHeadShot"] = int(processed_data.get("longestHeadShot", 0))

    # 创建 PlayerStats 对象
    player_stats = PlayerStats.from_dict(processed_data)

    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(raw_data["__update_time"]))

    # 整理武器数据，返回实体对象列表
    weapons_objects = prepare_weapons_data(raw_data, 50, game)

    # 将实体对象转换回字典，以便 Jinja2 模板渲染
    player_stats_dict = player_stats.to_dict()
    weapon_data_dicts = [w.to_dict() for w in weapons_objects] if weapons_objects else None

    html = WEAPONS_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=player_stats_dict, # 传递 PlayerStats 对象的字典表示
        weapon_data=weapon_data_dicts,
        game=game,
        background_color=background_color,
    )
    return html


def bf_vehicles_html_builder(raw_data: dict, game: str) -> str:
    """
    构建载具html
    Args:
        raw_data: 查询到的原始数据字典
        game: 所查询的游戏
    Returns:
        构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BFV_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF3_BACKGROUND_COLOR)

    # 预处理原始数据，使其符合 PlayerStats.from_dict 的期望
    processed_data = raw_data.copy()
    if processed_data.get("avatar") is None:
        processed_data["avatar"] = ImageUrls.DEFAULT_AVATAR
    
    # 计算 hoursPlayed 并添加到 processed_data，以便 PlayerStats.from_dict 使用
    processed_data["__hoursPlayed"] = str(round(processed_data.get("secondsPlayed", 0) / 3600, 1))
    processed_data["revives"] = int(processed_data.get("revives", 0))
    processed_data["longestHeadShot"] = int(processed_data.get("longestHeadShot", 0))

    # 创建 PlayerStats 对象
    player_stats = PlayerStats.from_dict(processed_data)

    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(raw_data["__update_time"]))

    # 整理载具数据，返回实体对象列表
    vehicles_objects = prepare_vehicles_data(raw_data, 50)

    # 将实体对象转换回字典，以便 Jinja2 模板渲染
    player_stats_dict = player_stats.to_dict()
    vehicle_data_dicts = [v.to_dict() for v in vehicles_objects] if vehicles_objects else None

    html = VEHICLES_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        d=player_stats_dict, # 传递 PlayerStats 对象的字典表示
        vehicle_data=vehicle_data_dicts,
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
