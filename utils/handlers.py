from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger

from typing import Union, Pattern
from data.plugins.astrbot_plugin_battlefield_tool.utils.RequestUtil import (gl_request_api,check_image_url_status)
from data.plugins.astrbot_plugin_battlefield_tool.database.BattleFieldDBService import (
    BattleFieldDBService,
)
from data.plugins.astrbot_plugin_battlefield_tool.utils.template import (
    bf_main_html_builder,
    bf_weapons_html_builder,
    bf_vehicles_html_builder,
    bf_servers_html_builder,
)

from dataclasses import dataclass
import re
import time


# 定义图片裁剪的通用参数
COMMON_CLIP_PARAMS = {"x": 0, "y": 0, "width": 700}


@dataclass
class PlayerDataRequest:
    message_str: str
    lang: str
    qq_id: str
    ea_name: Union[str, None]
    game: Union[str, None]
    server_name: Union[str, None]
    error_msg: Union[str, None]


class BattlefieldHandlers:
    def __init__(self, db_service: BattleFieldDBService, default_game: str, timeout_config: int, img_quality: int, session, default_platform: str = "pc"):
        self.db_service = db_service
        self.default_game = default_game
        self.timeout_config = timeout_config
        self.img_quality = img_quality
        self._session = session
        self.default_platform = default_platform # 添加默认平台配置
        self.LANG_CN = "zh-cn"
        self.LANG_TW = "zh-tw"
        self.SUPPORTED_GAMES = ["bf4","bf1", "bfv","bf6"]
        self.STAT_PATTERN = re.compile(
            r"^([\w-]*)(?:[，,]?game=([\w\-+.]+))?$"
        )

    def _get_session_channel_id(self, event: AstrMessageEvent) -> str:
        """根据事件类型获取会话渠道ID"""
        if not event.is_private_chat():
            return event.get_group_id()
        return event.get_sender_id()

    async def _resolve_game_tag(self, game_input: Union[str, None], session_channel_id: str) -> tuple[Union[str, None], Union[str, None]]:
        """
        解析游戏代号，获取默认值并进行验证。
        Returns:
            tuple: (game_tag, error_message)
        """
        game = game_input
        error_msg = None

        if game is None:
            bd_game = await self.db_service.query_session_channel(session_channel_id)
            if bd_game is None:
                game = self.default_game
            else:
                game = bd_game["default_game_tag"]

        if game == 'bf5':
            game = 'bfv'

        if game not in self.SUPPORTED_GAMES:
            error_msg = (
                f"服务器 '{game}' 未找到\n"
                f"• 请检查游戏代号是否正确\n"
                f"• 可用代号: {'、'.join(self.SUPPORTED_GAMES)}"
            )
            game = None # 确保在错误时返回None
        return game, error_msg

    async def _resolve_ea_name(self, ea_name_input: Union[str, None], qq_id: str) -> tuple[Union[str, None], Union[str, None]]:
        """
        解析EA账号名，获取默认值。
        Returns:
            tuple: (ea_name, error_message)
        """
        ea_name = ea_name_input
        error_msg = None

        if ea_name is None:
            bind_data = await self.db_service.query_bind_user(qq_id)
            if bind_data is None:
                error_msg = "请先使用bind [ea_name]绑定"
            else:
                ea_name = bind_data["ea_name"]
        return ea_name, error_msg

    async def _handle_bf6_stat(self, event: AstrMessageEvent, ea_name: str):
        """处理bf6的特殊查询逻辑"""
        bf6_img_url = f"https://drop-api.ea.com/player/{ea_name}/image?gameSlug=battlefield-6&eventName=OpenBetaWeekend2&aspectRatio=9x16&locale=zh-hans"
        res_code = await check_image_url_status(bf6_img_url)
        if res_code == 200:
            yield event.image_result(bf6_img_url)
        else:
            yield event.plain_result("此实验性功能，没有查询到，ea_name需要大小写完全匹配")

    def _handle_error_response(self, api_data: dict) -> Union[str, None]:
        """统一处理API响应中的错误信息"""
        if api_data is None:
            return "API调用失败，没有响应任何信息"
        if api_data.get("code") != 200:
            errors = api_data.get("errors")
            if errors and isinstance(errors, list) and len(errors) > 0:
                return errors[0]
            return "API返回未知错误"
        return None # 没有错误

    async def _process_api_response(self, event, api_data, data_type, game, html_render_func):
        """处理API响应通用逻辑"""
        error_msg = self._handle_error_response(api_data)
        if error_msg:
            yield event.plain_result(error_msg)
            return

        api_data["__update_time"] = time.time()

        # 根据数据类型调用对应的图片生成方法
        handler_map = {
            "stat": self._main_data_to_pic,
            "weapons": self._weapons_data_to_pic,
            "vehicles": self._vehicles_data_to_pic,
            "servers": self._servers_data_to_pic,
        }

        pic_url = await handler_map[data_type](api_data, game, html_render_func)
        yield event.image_result(pic_url)

    async def _handle_player_data_request(
        self, event: AstrMessageEvent, str_to_remove_list: list
    ) -> PlayerDataRequest:
        """
        从消息中提取参数
        Args:
            event: AstrMessageEvent
            str_to_remove_list: 去除指令
        Returns:
            PlayerDataRequest: 包含所有提取参数的数据类实例
        """
        message_str = event.message_str
        lang = self.LANG_CN
        qq_id = event.get_sender_id()
        session_channel_id = self._get_session_channel_id(event) # 使用辅助方法获取session_channel_id
        error_msg = None
        ea_name = None
        game = None
        server_name = None

        try:
            # 解析命令
            ea_name, game = await self._parse_input_regex(
                str_to_remove_list, self.STAT_PATTERN, message_str
            )
            # 由于共用解析方法所以这里赋个值
            if str_to_remove_list == ["servers", "服务器"]:
                server_name = ea_name
            
            # 处理游戏代号
            game, game_error = await self._resolve_game_tag(game, session_channel_id)
            if game_error:
                error_msg = game_error
                raise ValueError(error_msg) # 抛出异常以便被捕获

            # 处理EA账号名
            ea_name, ea_name_error = await self._resolve_ea_name(ea_name, qq_id)
            if ea_name_error:
                error_msg = ea_name_error
                raise ValueError(error_msg) # 抛出异常以便被捕获

            # 战地1使用繁中
            if game == "bf1":
                lang = self.LANG_TW
        except Exception as e:
            error_msg = str(e)

        return PlayerDataRequest(
            message_str=message_str,
            lang=lang,
            qq_id=qq_id,
            ea_name=ea_name,
            game=game,
            server_name=server_name,
            error_msg=error_msg,
        )

    @staticmethod
    async def _parse_input_regex(
        str_to_remove_list: list[str],
        pattern: Union[Pattern[str], None],
        base_string: str,
    ):
        """私有方法：从base_string中移除str_to_remove_list并去空格，然后根据正则取出参数
        Args:
            str_to_remove_list: 需要移除的子串list
            base_string: 原始字符串
        Returns:
            处理后的字符串
        """
        # 移除目标子串和空格
        for str_to_remove in str_to_remove_list:
            base_string = base_string.replace(str_to_remove, "")
        clean_str = base_string.replace(" ", "")
        # 用正则提取输入的参数
        if pattern is not None:
            match = pattern.match(clean_str.strip())
            if not match:
                raise ValueError("格式错误，正确格式：[用户名][,game=游戏名]")
            ea_name = match.group(1) or None
            game = match.group(2)
        else:
            ea_name = clean_str.strip()
            game = None
        return ea_name, game

    async def _main_data_to_pic(self, data: dict, game: str, html_render_func):
        """将查询的全部数据转为图片
        Args:
            data:查询到的战绩数据等
        Returns:
            返回生成的图片
        """
        html = bf_main_html_builder(data, game)
        url = await html_render_func(
            html,
            {},
            True,
            {
                "timeout": 10000,
                "quality": self.img_quality,
                "clip": {**COMMON_CLIP_PARAMS, "height": 2353},
            },
        )
        return url

    async def _weapons_data_to_pic(self, data: dict, game: str, html_render_func):
        """将查询的数据转为图片
        Args:
            data:查询到的战绩数据等
        Returns:
            返回生成的图片
        """
        html = bf_weapons_html_builder(data, game)
        url = await html_render_func(
            html,
            {},
            True,
            {
                "timeout": 10000,
                "quality": self.img_quality,
                "clip": {**COMMON_CLIP_PARAMS, "height": 10000},
            },
        )
        return url

    async def _vehicles_data_to_pic(self, data: dict, game: str, html_render_func):
        """将查询的数据转为图片
        Args:
            data:查询到的战绩数据等
        Returns:
            返回生成的图片
        """
        html = bf_vehicles_html_builder(data, game)
        url = await html_render_func(
            html,
            {},
            True,
            {
                "timeout": 10000,
                "quality": self.img_quality,
                "clip": {**COMMON_CLIP_PARAMS, "height": 10000},
            },
        )
        return url

    async def _servers_data_to_pic(self, data: dict, game: str, html_render_func):
        """将查询的服务器数据转为图片
        Args:
            data:查询到的战绩数据等
        Returns:
            返回生成的图片
        """
        # 数据量较少时设置高度
        height = 10000
        if data["servers"] is not None and len(data["servers"]) == 1:
            height = 450
        elif data["servers"] is not None and len(data["servers"]) == 2:
            height = 620
        html = bf_servers_html_builder(data, game)
        url = await html_render_func(
            html,
            {},
            True,
            {
                "timeout": 10000,
                "quality": self.img_quality,
                "clip": {**COMMON_CLIP_PARAMS, "height": height},
            },
        )
        return url
