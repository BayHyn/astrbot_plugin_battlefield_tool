"""
战地游戏相关常量
"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class ImageUrls:
    """图片URL常量类"""
    # 游戏Logo
    BF3_LOGO = "https://s21.ax1x.com/2025/07/19/pV3I9ET.png"
    BF4_LOGO = "https://s21.ax1x.com/2025/07/19/pV3IRaT.png"
    BF1_LOGO = "https://s21.ax1x.com/2025/07/19/pV35O3j.png"
    BFV_LOGO = "https://s21.ax1x.com/2025/07/19/pV35LCQ.png"

    # 游戏Banner
    BF3_BANNER = "https://s21.ax1x.com/2025/07/16/pV1jG5t.jpg"
    BF4_BANNER = "https://s21.ax1x.com/2025/07/16/pV1XV1S.jpg"
    BF1_BANNER = "https://s1.ax1x.com/2022/12/15/zoMaxe.jpg"
    BFV_BANNER = "https://s1.ax1x.com/2022/12/14/z54oIs.jpg"
    BF2042_BANNER = "https://s1.ax1x.com/2023/01/24/pSYXS3Q.jpg"

    # 默认头像
    DEFAULT_AVATAR = "https://s21.ax1x.com/2025/07/16/pV1Ox6e.jpg"

    # 错误图片修复URL
    ERROR_IMG = [
        {"name": "su-50", "repair_url": "https://s21.ax1x.com/2025/07/23/pVGGFeK.png"},
        {"name": "lav-25", "repair_url": "https://s21.ax1x.com/2025/08/13/pVwK8dP.png"},
        {"name": "lav-ad", "repair_url": "https://s21.ax1x.com/2025/08/13/pVwKUzQ.png"},
    ]

    # 其他静态图片
    SU_50 = "https://s21.ax1x.com/2025/07/23/pVGGFeK.png"

    @classmethod
    def get_all_static_urls(cls) -> dict:
        """获取所有静态图片URL映射"""
        return {
            "bf4_logo": cls.BF4_LOGO,
            "bf1_logo": cls.BF1_LOGO,
            "bfv_logo": cls.BFV_LOGO,
            "bf4_banner": cls.BF4_BANNER,
            "bf1_banner": cls.BF1_BANNER,
            "bfv_banner": cls.BFV_BANNER,
            "default_avatar": cls.DEFAULT_AVATAR,
            "su_50": cls.SU_50
        }


class BackgroundColors:
    """背景色常量类"""
    BF3_BACKGROUND_COLOR = "#111B2B"
    BF4_BACKGROUND_COLOR = "#111B2B"
    BF1_BACKGROUND_COLOR = "rgb(139 81 41)"
    BFV_BACKGROUND_COLOR = "rgb(38 62 112)"
    BF2042_BACKGROUND_COLOR = "#111B2B"


class GameMappings:
    """游戏映射常量类"""
    # Banner映射
    BANNERS = {
        "bf3": ImageUrls.BF3_BANNER,
        "bf4": ImageUrls.BF4_BANNER,
        "bf1": ImageUrls.BF1_BANNER,
        "bfv": ImageUrls.BFV_BANNER,
        "bf2042": ImageUrls.BF2042_BANNER,
    }

    # 背景色映射
    BACKGROUND_COLORS = {
        "bf3": BackgroundColors.BF3_BACKGROUND_COLOR,
        "bf4": BackgroundColors.BF4_BACKGROUND_COLOR,
        "bf1": BackgroundColors.BF1_BACKGROUND_COLOR,
        "bfv": BackgroundColors.BFV_BACKGROUND_COLOR,
        "bf2042": BackgroundColors.BF2042_BACKGROUND_COLOR,
    }

    # Logo映射
    LOGOS = {
        "bf3": ImageUrls.BF3_LOGO,
        "bf4": ImageUrls.BF4_LOGO,
        "bf1": ImageUrls.BF1_LOGO,
        "bfv": ImageUrls.BFV_LOGO,
    }


class TemplateConstants:
    """模板常量类"""
    PARENT_FOLDER = Path(__file__).parent.parent.resolve()
    
    @classmethod
    def get_template_env(cls):
        """获取Jinja2模板环境"""
        template_dir = cls.PARENT_FOLDER / "template"
        return Environment(loader=FileSystemLoader(template_dir))
    
    @classmethod
    def get_templates(cls):
        """获取所有模板"""
        env = cls.get_template_env()
        return {
            "main": env.get_template("template.html"),
            "weapons": env.get_template("template_weapons.html"),
            "vehicles": env.get_template("template_vehicles.html"),
            "servers": env.get_template("template_servers.html"),
            "weapon_card": env.get_template("weapon_card.html"),
            "vehicle_card": env.get_template("vehicle_card.html"),
            "server_card": env.get_template("server_card.html"),
        }
