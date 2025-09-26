from astrbot.api import logger
from ..constants.battlefield_constants import (ImageUrls, BackgroundColors, GameMappings, TemplateConstants)
from ..models.btr_entities import PlayerStats, Weapon, Vehicle, Soldier  # 导入实体类

import time

# 获取模板
templates = TemplateConstants.get_templates()
MAIN_TEMPLATE = templates["btr_main"]
WEAPONS_TEMPLATE = templates["btr_weapons"]
VEHICLES_TEMPLATE = templates["btr_vehicles"]
SOLDIERS_TEMPLATE = templates["btr_soldiers"]


def sort_list_of_dicts(list_of_dicts, key):
    """降序排序，支持点分隔的嵌套键，如果值为零就删除该项"""
    def get_nested_value(d, k_path):
        keys = k_path.split('.')
        current_value = d
        for key_part in keys:
            if isinstance(current_value, dict) and key_part in current_value:
                current_value = current_value[key_part]
            else:
                # 如果路径无效，返回一个默认值，例如0，以便排序不会失败
                return 0
        return current_value

    # 先过滤掉值为零的项
    filtered_list = [d for d in list_of_dicts if get_nested_value(d, key) != 0]
    
    # 然后对过滤后的列表进行降序排序
    return sorted(filtered_list, key=lambda k: get_nested_value(k, key), reverse=True)


def btr_main_html_builder(stat_data: dict, weapons_data, vehicles_data, soldier_data, game: str) -> str:
    """
        构建主要html
        Args:
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的专家数据字典
            game: 所查询的游戏
        Returns:
            构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BF2042_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF2042_BACKGROUND_COLOR)
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 创建对象
    stat_entity = PlayerStats.from_btr_dict(stat_data)
    stat_entity.avatar = ImageUrls().DEFAULT_AVATAR
    logger.info(f"Default avatar URL: {stat_entity.avatar}")

    weapons_data = sort_list_of_dicts(weapons_data, "stats.kills.value")
    vehicles_data = sort_list_of_dicts(vehicles_data, "stats.kills.value")
    soldier_data = sort_list_of_dicts(soldier_data, "stats.kills.value")

    # 循环创建武器、载具、专家对象列表
    weapons_entities = [Weapon.from_btr_dict(weapon_dict) for weapon_dict in weapons_data[:3]]
    vehicles_entities = [Vehicle.from_btr_dict(vehicle_dict) for vehicle_dict in vehicles_data[:3]]
    soldiers_entities = [Soldier.from_btr_dict(soldier_dict) for soldier_dict in soldier_data[:1]]

    html = MAIN_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        stat_entity=stat_entity,
        weapon_data=weapons_entities,
        vehicle_data=vehicles_entities,
        soldier_data=soldiers_entities,
        game=game,
        background_color=background_color,
    )
    return html


def btr_weapons_html_builder(stat_data: dict, weapons_data,vehicles_data, soldier_data, game: str) -> str:
    """
        构建武器html
        Args:
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的专家数据字典
            game: 所查询的游戏
        Returns:
            构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BF2042_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF2042_BACKGROUND_COLOR)
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 创建对象
    stat_entity = PlayerStats.from_btr_dict(stat_data)
    stat_entity.avatar = ImageUrls().DEFAULT_AVATAR
    logger.info(f"Default avatar URL: {stat_entity.avatar}")

    weapons_data = sort_list_of_dicts(weapons_data, "stats.kills.value")

    # 循环创建武器、载具、专家对象列表
    weapons_entities = [Weapon.from_btr_dict(weapon_dict) for weapon_dict in weapons_data]

    html = WEAPONS_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        stat_entity=stat_entity,
        weapon_data=weapons_entities,
        game=game,
        background_color=background_color,
    )
    return html


def btr_vehicles_html_builder(stat_data: dict,weapons_data, vehicles_data,soldier_data, game: str) -> str:
    """
        构建载具html
        Args:
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的专家数据字典
            game: 所查询的游戏
        Returns:
            构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BF2042_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF2042_BACKGROUND_COLOR)
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 创建对象
    stat_entity = PlayerStats.from_btr_dict(stat_data)
    stat_entity.avatar = ImageUrls().DEFAULT_AVATAR
    logger.info(f"Default avatar URL: {stat_entity.avatar}")

    vehicles_data = sort_list_of_dicts(vehicles_data, "stats.kills.value")

    # 循环创建武器、载具、专家对象列表
    vehicles_entities = [Vehicle.from_btr_dict(vehicle_dict) for vehicle_dict in vehicles_data]

    html = VEHICLES_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        stat_entity=stat_entity,
        vehicle_data=vehicles_entities,
        game=game,
        background_color=background_color,
    )
    return html


def btr_soldier_html_builder(stat_data: dict,weapons_data, vehicles_data, soldier_data, game: str) -> str:
    """
        构建专家html
        Args:
            stat_data: 查询到的统计数据字典
            weapons_data: 查询到的武器数据字典
            vehicles_data: 查询到的载具数据字典
            soldier_data: 查询到的专家数据字典
            game: 所查询的游戏
        Returns:
            构建的Html
    """
    banner = GameMappings.BANNERS.get(game, ImageUrls.BF2042_BANNER)
    background_color = GameMappings.BACKGROUND_COLORS.get(game, BackgroundColors.BF2042_BACKGROUND_COLOR)
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 创建对象
    stat_entity = PlayerStats.from_btr_dict(stat_data)
    stat_entity.avatar = ImageUrls().DEFAULT_AVATAR
    logger.info(f"Default avatar URL: {stat_entity.avatar}")

    soldier_data = sort_list_of_dicts(soldier_data, "stats.kills.value")

    # 循环创建专家对象列表
    soldiers_entities = [Soldier.from_btr_dict(soldier_dict) for soldier_dict in soldier_data]

    html = SOLDIERS_TEMPLATE.render(
        banner=banner,
        update_time=update_time,
        stat_entity=stat_entity,
        soldier_data=soldiers_entities,
        game=game,
        background_color=background_color,
    )
    return html
