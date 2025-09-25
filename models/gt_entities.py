from typing import List, Optional, Dict, Any

class PlayerStats:
    """
    对应 template.html 中 'd' 对象的数据结构。
    包含玩家的基本统计信息。
    """
    def __init__(self,
                 avatar: str, # 玩家头像URL
                 user_name: str, # 玩家用户名
                 rank_img: str, # 玩家等级图片URL
                 rank: str, # 玩家等级
                 hours_played: str, # 游戏时间（小时）
                 kills: int, # 击杀数
                 kill_death: str, # 击杀/死亡比
                 kills_per_minute: str, # 每分钟击杀数
                 headshots: str, # 爆头率
                 accuracy: str, # 命中率
                 revives: str, # 急救数
                 head_shots_num: str, # 爆头数
                 longest_head_shot: str, # 最远爆头距离（米）
                 wins: str, # 胜利场次
                 highest_kill_streak: str): # 最高连杀数
        self.avatar = avatar
        self.user_name = user_name
        self.rank_img = rank_img
        self.rank = rank
        self.hours_played = hours_played
        self.kills = kills
        self.kill_death = kill_death
        self.kills_per_minute = kills_per_minute
        self.headshots = headshots
        self.accuracy = accuracy
        self.revives = revives
        self.head_shots_num = head_shots_num
        self.longest_head_shot = longest_head_shot
        self.wins = wins
        self.highest_kill_streak = highest_kill_streak

    @classmethod
    def from_gt_dict(cls, data: Dict[str, Any]):
        """从gt字典创建 PlayerStats 实例"""
        return cls(
            avatar=data.get("avatar", ""),
            user_name=data.get("userName", "N/A"),
            rank_img=data.get("rankImg", ""),
            rank=str(data.get("rank", 0)),
            hours_played=str(data.get("__hours_played", 0.0)), # 注意这里是 __hours_played
            kills=int(data.get("kills", 0)),
            kill_death=str(data.get("killDeath", 0.0)),
            kills_per_minute=str(data.get("killsPerMinute", 0.0)),
            headshots=str(data.get("headshots", 0.0)),
            accuracy=str(data.get("accuracy", 0.0)),
            revives=str(data.get("revives", 0)),
            head_shots_num=str(data.get("headShots", 0)),
            longest_head_shot=str(data.get("longestHeadShot", 0.0)),
            wins=str(data.get("wins", 0)),
            highest_kill_streak=str(data.get("highestKillStreak", 0))
        )

    def to_dict(self) -> Dict[str, Any]:
        """将 PlayerStats 实例转换为字典"""
        return {
            "avatar": self.avatar,
            "user_name": self.user_name,
            "rank_img": self.rank_img,
            "rank": str(self.rank),
            "__hours_played": str(self.hours_played),
            "kills": int(self.kills),
            "kill_death": str(self.kill_death),
            "kills_per_minute": str(self.kills_per_minute),
            "headshots": str(self.headshots),
            "accuracy": str(self.accuracy),
            "revives": str(self.revives),
            "head_shots_num": str(self.head_shots_num),
            "longest_head_shot": str(self.longest_head_shot),
            "wins": str(self.wins),
            "highest_kill_streak": str(self.highest_kill_streak)
        }

    def __repr__(self):
        return f"PlayerStats(user_name='{self.user_name}', rank={self.rank}, ...)"


class Weapon:
    """
    对应 weapon_card.html 中 'w' 对象的数据结构。
    包含武器的详细信息。
    """
    def __init__(self,
                 name: str, # 武器名称
                 image: str, # 武器图片URL
                 kills: int, # 武器击杀数
                 headshotKills: int, # 爆头击杀数
                 shotsFired: int, # 击发数
                 shotsHit: int, # 命中数
                 headshots: str, # 爆头率
                 accuracy: str, # 命中率
                 kills_per_minute: str, # 武器每分钟击杀数
                 timeSpent: str, # 武器装备时间（小时）
                 type: str): # 武器类型
        self.name = name
        self.image = image
        self.kills = kills
        self.headshotKills = headshotKills
        self.shotsFired = shotsFired
        self.shotsHit = shotsHit
        self.headshots = headshots
        self.accuracy = accuracy
        self.kills_per_minute = kills_per_minute
        self.timeSpent = timeSpent
        self.type = type

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建 Weapon 实例"""
        return cls(
            name=data.get("name", "N/A"),
            image=data.get("image", ""),
            kills=int(data.get("kills", 0)),
            headshotKills=int(data.get("headshotKills", 0)),
            shotsFired=int(data.get("shotsFired", 0)),
            shotsHit=int(data.get("shotsHit", 0)),
            headshots=str(data.get("headshots", 0)),
            accuracy=str(data.get("accuracy", 0.0)),
            kills_per_minute=str(data.get("killsPerMinute", "0.0")),
            timeSpent=str(data.get("timeSpent", "0.0")),
            type=data.get("type", "Unknown")
        )

    def to_dict(self) -> Dict[str, Any]:
        """将 Weapon 实例转换为字典"""
        return {
            "name": self.name,
            "image": self.image,
            "kills": int(self.kills),
            "headshotKills": int(self.headshotKills),
            "shotsFired": int(self.shotsFired),
            "shotsHit": int(self.shotsHit),
            "headshots": str(self.headshots),
            "accuracy": str(self.accuracy),
            "kills_per_minute": str(self.kills_per_minute),
            "timeSpent": str(self.timeSpent),
            "type": str(self.type)
        }

    def __repr__(self):
        return f"Weapon(name='{self.name}', kills={self.kills}, ...)"


class Vehicle:
    """
    对应 vehicle_card.html 中 'v' 对象的数据结构。
    包含载具的详细信息。
    """
    def __init__(self,
                 name: str, # 载具名称
                 image: str, # 载具图片URL
                 kills: int, # 载具击杀数
                 destroyed: str, # 载具摧毁数
                 kills_per_minute: str, # 载具每分钟击杀数
                 timeSpent: str, # 载具使用时间（小时）
                 type: str): # 载具类型
        self.name = name
        self.image = image
        self.kills = kills
        self.destroyed = destroyed
        self.kills_per_minute = kills_per_minute
        self.timeSpent = timeSpent
        self.type = type

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建 Vehicle 实例"""
        return cls(
            name=data.get("name", "N/A"),
            image=data.get("image", ""),
            kills=int(data.get("kills", 0)),
            destroyed=str(data.get("destroyed", 0)),
            kills_per_minute=str(data.get("killsPerMinute", "0.0")),
            timeSpent=str(data.get("timeSpent", "0.0")),
            type=data.get("type", "Unknown")
        )

    def to_dict(self) -> Dict[str, Any]:
        """将 Vehicle 实例转换为字典"""
        return {
            "name": self.name,
            "image": self.image,
            "kills": int(self.kills),
            "destroyed": str(self.destroyed),
            "kills_per_minute": str(self.kills_per_minute),
            "timeSpent": str(self.timeSpent),
            "type": str(self.type)
        }

    def __repr__(self):
        return f"Vehicle(name='{self.name}', kills={self.kills}, ...)"
