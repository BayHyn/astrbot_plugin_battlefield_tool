from astrbot.api.event import AstrMessageEvent
from astrbot.api import logger

from ..core.request_util import (gt_request_api, btr_request_api)
from ..core.plugin_logic import PlayerDataRequest, BattlefieldPluginLogic


class ApiHandlers:
    def __init__(self, plugin_logic: BattlefieldPluginLogic, html_render_func, timeout_config: int, ssc_token: str,
                 session):
        self.plugin_logic = plugin_logic
        self.html_render = html_render_func
        self.timeout_config = timeout_config
        self.ssc_token = ssc_token
        self._session = session

    async def fetch_gt_data(self, event: AstrMessageEvent, request_data: PlayerDataRequest, data_type: str,
                            prop: str = None,is_llm:bool = False):
        """
        根据游戏类型获取数据并处理响应 (非bf6/bf2042)。
        """
        api_data = await gt_request_api(
            request_data.game,
            prop,
            {"name": request_data.ea_name, "lang": request_data.lang, "platform": self.plugin_logic.default_platform},
            self.timeout_config,
            session=self._session,
        )

        async for result in self.plugin_logic.process_api_response(
                event, api_data, data_type, request_data.game, self.html_render,is_llm
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
            "bf6_stat": "/bf6/stat",
        }
        btr_prop = btr_prop_map.get(data_type)
        if btr_prop is None:
            yield event.plain_result(f"不支持的游戏类型 '{data_type}' 用于bf6/bf2042查询。")
            return

        # 士兵查询仅限bf2042
        if data_type == "soldier" and request_data.game != "bf2042":
            yield event.plain_result("士兵查询目前仅支持战地2042。")
            return

        api_data = await btr_request_api(
            btr_prop,
            {"player_name": request_data.ea_name, "game": request_data.game},
            self.timeout_config,
            self.ssc_token,
            session=self._session,
        )
        yield api_data

    async def handle_btr_game(self, event: AstrMessageEvent, request_data: PlayerDataRequest, prop,
                              is_llm: bool = False):
        """处理BTR游戏（bf2042, bf6）的统计数据查询"""
        stat_data = None
        weapon_data = []
        vehicle_data = []
        soldier_data = []

        if request_data.game == "bf6":
            async for data in self._fetch_btr_data(event, request_data, "bf6_stat"):
                stat_data = data
                result_data = data.get("segments")
                for result in result_data:
                    if result["type"] == "kit":
                        soldier_data.append(result)
                        continue
                    if result["type"] == "weapon":
                        weapon_data.append(result)
                        continue
                    if result["type"] == "vehicle":
                        vehicle_data.append(result)
                        continue

        else:
            async for data in self._fetch_btr_data(event, request_data, "stat"):
                stat_data = data

            if prop in ["stat", "weapons"]:
                async for data in self._fetch_btr_data(event, request_data, "weapons"):
                    weapon_data = data

            if prop in ["stat", "vehicles"]:
                async for data in self._fetch_btr_data(event, request_data, "vehicles"):
                    vehicle_data = data

            if prop in ["stat", "soldiers"]:
                async for data in self._fetch_btr_data(event, request_data, "soldiers"):
                    soldier_data = data

        async for result in self.plugin_logic.handle_btr_response(event, prop, request_data.game,
                                                                  self.html_render, stat_data, weapon_data,
                                                                  vehicle_data, soldier_data, is_llm):
            yield result

    async def fetch_gt_servers_data(self, request_data: PlayerDataRequest, timeout_config: int, session):
        """
        获取GT服务器数据。
        """
        servers_data = await gt_request_api(
            request_data.game,
            "servers",
            {
                "name": request_data.server_name,
                "lang": request_data.lang,
                "platform": self.plugin_logic.default_platform,
                "region": "all",
                "limit": 30,
            },
            timeout_config,
            session=session,
        )
        return servers_data

    async def check_ea_name(self, request_data: PlayerDataRequest, timeout_config: int, session):
        """检查ea_name正确性，并返回pid"""
        stats_data = await gt_request_api(
            "bfv",
            "stats",
            {
                "name": request_data.ea_name,
                "platform": self.plugin_logic.default_platform,
            },
            timeout_config,
            session=session,
        )
        if stats_data is None:
            return stats_data.get("userId")
        else:
            return None