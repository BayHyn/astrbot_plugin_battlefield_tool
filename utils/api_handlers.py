from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger

from ..utils.request_util import (gt_request_api, btr_request_api)
from ..utils.plugin_logic import PlayerDataRequest, BattlefieldPluginLogic



class ApiHandlers:
    def __init__(self, handlers: BattlefieldPluginLogic, html_render_func, timeout_config: int, ssc_token: str, session):
        self.handlers = handlers
        self.html_render = html_render_func
        self.timeout_config = timeout_config
        self.ssc_token = ssc_token
        self._session = session

    async def _process_api_response_and_yield(self, event: AstrMessageEvent, api_data, data_type: str, game: str):
        """
        处理API响应并yield结果
        """
        async for result in self.handlers._process_api_response(
                event, api_data, data_type, game, self.html_render
        ):
            yield result

    async def _process_btr_response_and_yield(self, event: AstrMessageEvent, data_type: str, game: str,
                                            stat_data, weapon_data, vehicle_data, soldier_data):
        """
        处理BTR响应并yield结果
        """
        async for result in self.handlers._handle_btr_response(
                event, data_type, game, self.html_render, stat_data, weapon_data, vehicle_data, soldier_data
        ):
            yield result

    async def _fetch_gt_data(self, event: AstrMessageEvent, request_data: PlayerDataRequest, data_type: str,
                             prop: str = None):
        """
        根据游戏类型获取数据并处理响应 (非bf6/bf2042)。
        """
        api_data = await gt_request_api(
            request_data.game,
            prop,
            {"name": request_data.ea_name, "lang": request_data.lang, "platform": self.handlers.default_platform},
            self.timeout_config,
            session=self._session,
        )

        async for result in self._process_api_response_and_yield(
                event, api_data, data_type, request_data.game
        ):
            yield result

    async def _fetch_btr_data(self, event: AstrMessageEvent, request_data: PlayerDataRequest, data_type: str):
        """
        根据游戏类型获取数据并处理响应 (bf6/bf2042)。
        """
        btr_prop_map = {
            "stat": "/player/stat",
            "weapons": "/player/weapons",
            "vehicles": "/player/vehicles",
            "soldiers": "/player/soldiers",
        }
        btr_prop = btr_prop_map.get(data_type)
        if btr_prop is None:
            yield event.plain_result(f"不支持的游戏类型 '{data_type}' 用于bf6/bf2042查询。")
            return

        # 专家查询仅限bf2042
        if data_type == "soldier" and request_data.game != "bf2042":
            yield event.plain_result("专家查询目前仅支持战地2042。")
            return

        api_data = await btr_request_api(
            btr_prop,
            {"player_name": request_data.ea_name, "game": request_data.game},
            self.timeout_config,
            self.ssc_token,
            session=self._session,
        )
        yield api_data

    async def _handle_btr_game(self, event: AstrMessageEvent, request_data: PlayerDataRequest, prop):
        """处理BTR游戏（bf2042, bf6）的统计数据查询"""
        stat_data = None
        async for data in self._fetch_btr_data(event, request_data, "stat"):
            stat_data = data

        weapon_data = None
        if prop in ["stat", "weapons"]:
            async for data in self._fetch_btr_data(event, request_data, "weapons"):
                weapon_data = data

        vehicle_data = None
        if prop in ["stat", "vehicles"]:
            async for data in self._fetch_btr_data(event, request_data, "vehicles"):
                vehicle_data = data

        soldier_data = None
        if prop in ["stat", "soldiers"]:
            async for data in self._fetch_btr_data(event, request_data, "soldiers"):
                soldier_data = data

        async for result in self._process_btr_response_and_yield(event, prop, request_data.game,
                                                                  stat_data, weapon_data, vehicle_data, soldier_data):
            yield result

    async def _fetch_gt_servers_data(self, request_data: PlayerDataRequest, timeout_config: int, session):
        """
        获取GT服务器数据。
        """
        servers_data = await gt_request_api(
            request_data.game,
            "servers",
            {
                "name": request_data.server_name,
                "lang": request_data.lang,
                "platform": self.handlers.default_platform,
                "region": "all",
                "limit": 30,
            },
            timeout_config,
            session=session,
        )
        return servers_data
