import time

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, StarTools, register
from astrbot.api.all import AstrBotConfig
from astrbot.api import logger

from typing import Union
from data.plugins.astrbot_plugin_battlefield_tool.utils.RequestUtil import (gl_request_api,check_image_url_status)
from data.plugins.astrbot_plugin_battlefield_tool.database.BattleFieldDataBase import (
    BattleFieldDataBase,
)
from data.plugins.astrbot_plugin_battlefield_tool.database.BattleFieldDBService import (
    BattleFieldDBService,
)
from data.plugins.astrbot_plugin_battlefield_tool.utils.handlers import BattlefieldHandlers, PlayerDataRequest

import aiohttp


@register(
    "astrbot_plugin_battlefield_tool",  # name
    "SHOOTING_STAR_C",  # author
    "战地风云战绩查询插件",  # desc
    "v1.0.9",  # version
)
class BattlefieldTool(Star):

    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config

        # 防御性配置处理：如果config为None，使用默认值
        if config is None:
            logger.warning("BattlefieldTool: 未提供配置文件，将使用默认配置")
            self.default_game = "bfv"
            self.timeout_config = 15
            self.img_quality = 90
        else:
            logger.debug("BattlefieldTool: 使用用户配置文件")
            self.default_game = config.get("default_game", "bfv")
            self.timeout_config = config.get("timeout_config", 15)
            self.img_quality = config.get("img_quality", 90)

        self.bf_data_path = StarTools.get_data_dir("battleField_tool_plugin")
        self.db = BattleFieldDataBase(self.bf_data_path)  # 初始化数据库
        self.db_service = BattleFieldDBService(self.db)  # 初始化数据库服务
        self._session = None
        self.default_platform = "pc" # 默认平台
        self.handlers = BattlefieldHandlers(self.db_service, self.default_game, self.timeout_config, self.img_quality, self._session, self.default_platform)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        self._session = aiohttp.ClientSession()
        await self.db.initialize()  # 添加数据库初始化调用
        self.handlers._session = self._session # 更新handlers中的session

    @filter.command("stat")
    async def bf_stat(self, event: AstrMessageEvent):
        """查询用户数据"""
        request_data = await self.handlers._handle_player_data_request(event, ["stat"])

        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return

        logger.info(f"玩家id:{request_data.ea_name}，所查询游戏:{request_data.game}")
        if request_data.game == 'bf6':
            async for result in self.handlers._handle_bf6_stat(event, request_data.ea_name):
                yield result
            return
        player_data = await gl_request_api(
            request_data.game,
            "all",
            {"name": request_data.ea_name, "lang": request_data.lang, "platform": self.handlers.default_platform},
            self.timeout_config,
            session=self._session,
        )

        async for result in self.handlers._process_api_response(
            event, player_data, "stat", request_data.game, self.html_render
        ):
            yield result

    @filter.command("weapons", alias=["武器"])
    async def bf_weapons(self, event: AstrMessageEvent):
        """查询用户武器数据"""
        request_data = await self.handlers._handle_player_data_request(event, ["weapons", "武器"])

        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return

        logger.info(f"玩家id:{request_data.ea_name}，所查询游戏:{request_data.game}")
        player_data = await gl_request_api(
            request_data.game,
            "weapons",
            {"name": request_data.ea_name, "lang": request_data.lang, "platform": self.handlers.default_platform},
            self.timeout_config,
            session=self._session,
        )

        async for result in self.handlers._process_api_response(
            event, player_data, "weapons", request_data.game, self.html_render
        ):
            yield result

    @filter.command("vehicles", alias=["载具"])
    async def bf_vehicles(self, event: AstrMessageEvent):
        """查询载具数据"""
        request_data = await self.handlers._handle_player_data_request(event, ["vehicles", "载具"])

        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return

        logger.info(f"玩家id:{request_data.ea_name}，所查询游戏:{request_data.game}")
        player_data = await gl_request_api(
            request_data.game,
            "vehicles",
            {"name": request_data.ea_name, "lang": request_data.lang, "platform": self.handlers.default_platform},
            self.timeout_config,
            session=self._session,
        )

        async for result in self.handlers._process_api_response(
            event, player_data, "vehicles", request_data.game, self.html_render
        ):
            yield result

    @filter.command("servers", alias=["服务器"])
    async def bf_servers(self, event: AstrMessageEvent):
        """查询服务器数据"""
        request_data = await self.handlers._handle_player_data_request(event, ["servers", "服务器"])

        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return
        if request_data.server_name is None:
            yield event.plain_result("请提供服务器名称进行查询哦~") # 优化提示信息
            return

        logger.info(f"查询服务器:{request_data.server_name}，所查询游戏:{request_data.game}")
        servers_data = await gl_request_api(
            request_data.game,
            "servers",
            {
                "name": request_data.server_name,
                "lang": request_data.lang,
                "platform": self.handlers.default_platform,
                "region": "all",
                "limit": 30,
            },
            self.timeout_config,
            session=self._session,
        )

        # 特殊处理服务器空数据情况
        if servers_data is None:
            yield event.plain_result("API调用失败，没有响应任何信息")
            return

        if servers_data.get("code") != 200:
            yield event.plain_result(servers_data.get("errors")[0])
            return

        if servers_data["servers"] is not None and len(servers_data["servers"]) > 0:
            servers_data["__update_time"] = time.time()
            pic_url = await self.handlers._servers_data_to_pic(servers_data, request_data.game, self.html_render)
            yield event.image_result(pic_url)
        else:
            yield event.plain_result("暂无数据")

    @filter.command("bind", alias=["绑定"])
    async def bf_bind(self, event: AstrMessageEvent):
        """绑定本插件默认查询的用户"""
        request_data = await self.handlers._handle_player_data_request(event, ["bind", "绑定"])
        if request_data.error_msg:
            yield event.plain_result(request_data.error_msg)
            return
        # 调用bfv的接口查询用户是否存在
        player_data = await gl_request_api(
            self.default_game,
            "stats",
            {"name": request_data.ea_name, "lang": "zh-cn", "platform": self.handlers.default_platform},
            self.timeout_config,
            session=self._session,
        )
        if player_data is None:
            yield event.plain_result("API调用失败，没有响应任何信息")
            return

        if player_data.get("code") != 200:
            yield event.plain_result(player_data.get("errors")[0])
            return

        if player_data.get("code") == 200:
            ea_id = player_data["userId"]
            logger.debug(f"已查询到{request_data.ea_name}的ea_id：{ea_id}")
            # 持久化绑定数据
            msg = await self.db_service.upsert_user_bind(request_data.qq_id, request_data.ea_name, ea_id)
            yield event.plain_result(msg)

    @filter.command("bf_init")
    async def bf_init(self, event: AstrMessageEvent):
        """同一机器人不同会话渠道配置不同的默认查询"""
        message_str = event.message_str
        session_channel_id = self.handlers._get_session_channel_id(event)

        if not event.is_private_chat():
            # 群聊只能机器人管理员设置渠道绑定命令
            if not event.is_admin():
                yield event.plain_result(
                    "没有权限哦，群聊只能机器人管理员使用[bf_init]命令呢"
                )
                return

            session_channel_id = event.get_group_id()

        # 解析命令，直接提取游戏代号
        command_prefix = ["bf_init"]
        clean_str = message_str
        for prefix in command_prefix:
            clean_str = clean_str.replace(prefix, "")
        default_game = clean_str.strip()

        if not default_game:
            yield event.plain_result("不能设置空哦~")
        else:
            # 持久化渠道数据
            msg = await self.db_service.upsert_session_channel(
                session_channel_id, default_game
            )
            yield event.plain_result(msg)

    @filter.command("bf_help")
    async def bf_help(self, event: AstrMessageEvent):
        """显示战地插件帮助信息"""
        help_msg = f"""战地风云插件使用帮助：
1. 账号绑定
命令: {{唤醒词}}bind [ea_name] 或 {{唤醒词}}绑定 [ea_name]
参数: ea_name - 您的EA账号名
示例: {{唤醒词}}bind ExamplePlayer

2. 默认查询设置
命令: {{唤醒词}}bf_init [游戏代号]
参数: 游戏代号 {", ".join(self.handlers.SUPPORTED_GAMES)}
注意: 私聊都能使用，群聊中仅bot管理员可用

3. 战绩查询
命令: {{唤醒词}}stat [ea_name],game=[游戏代号]
参数:
  ea_name - EA账号名(可选，已绑定则可不填)
  game - 游戏代号(可选)
示例: {{唤醒词}}stat ExamplePlayer,game=bf1

4. 武器统计
命令: {{唤醒词}}weapons [ea_name],game=[游戏代号] 或 {{唤醒词}}武器 [ea_name],game=[游戏代号]
参数同上
示例: {{唤醒词}}weapons ExamplePlayer,game=bfv

5. 载具统计
命令: {{唤醒词}}vehicles [ea_name],game=[游戏代号] 或 {{唤醒词}}载具 [ea_name],game=[游戏代号]
参数同上
示例: {{唤醒词}}vehicles ExamplePlayer

6. 服务器查询
命令: {{唤醒词}}servers [server_name],game=[游戏代号] 或 {{唤醒词}}服务器 [server_name],game=[游戏代号]
参数:
  server_name - 服务器名称(必填)
  game - 游戏代号(可选)
示例: {{唤醒词}}servers 中文服务器,game=bf1

注: 实际使用时不需要输入[]。{{唤醒词}}为唤醒词，以实际情况为准
"""
        yield event.plain_result(help_msg)

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件卸载/停用时会调用。"""
        if self._session:
            await self._session.close()
