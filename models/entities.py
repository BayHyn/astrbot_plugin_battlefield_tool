from typing import List, Optional, Dict, Any

class PlayerStats:
    """
    对应 template.html 中 'd' 对象的数据结构。
    包含玩家的基本统计信息。
    """
    def __init__(self,
                 avatar: str, # 玩家头像URL
                 userName: str, # 玩家用户名
                 rankImg: str, # 玩家等级图片URL
                 rank: str, # 玩家等级
                 hoursPlayed: str, # 游戏时间（小时）
                 kills: int, # 击杀数
                 killDeath: str, # 击杀/死亡比
                 killsPerMinute: str, # 每分钟击杀数
                 headshots: str, # 爆头率
                 accuracy: str, # 命中率
                 revives: str, # 急救数
                 headShots: str, # 爆头数
                 longestHeadShot: str, # 最远爆头距离（米）
                 wins: str, # 胜利场次
                 highestKillStreak: str): # 最高连杀数
        self.avatar = avatar
        self.userName = userName
        self.rankImg = rankImg
        self.rank = rank
        self.hoursPlayed = hoursPlayed
        self.kills = kills
        self.killDeath = killDeath
        self.killsPerMinute = killsPerMinute
        self.headshots = headshots
        self.accuracy = accuracy
        self.revives = revives
        self.headShots = headShots
        self.longestHeadShot = longestHeadShot
        self.wins = wins
        self.highestKillStreak = highestKillStreak

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建 PlayerStats 实例"""
        return cls(
            avatar=data.get("avatar", ""),
            userName=data.get("userName", "N/A"),
            rankImg=data.get("rankImg", ""),
            rank=str(data.get("rank", 0)),
            hoursPlayed=str(data.get("__hoursPlayed", 0.0)), # 注意这里是 __hoursPlayed
            kills=int(data.get("kills", 0)),
            killDeath=str(data.get("killDeath", 0.0)),
            killsPerMinute=str(data.get("killsPerMinute", 0.0)),
            headshots=str(data.get("headshots", 0.0)),
            accuracy=str(data.get("accuracy", 0.0)),
            revives=str(data.get("revives", 0)),
            headShots=str(data.get("headShots", 0)),
            longestHeadShot=str(data.get("longestHeadShot", 0.0)),
            wins=str(data.get("wins", 0)),
            highestKillStreak=str(data.get("highestKillStreak", 0))
        )

    def to_dict(self) -> Dict[str, Any]:
        """将 PlayerStats 实例转换为字典"""
        return {
            "avatar": self.avatar,
            "userName": self.userName,
            "rankImg": self.rankImg,
            "rank": str(self.rank),
            "__hoursPlayed": str(self.hoursPlayed),
            "kills": int(self.kills),
            "killDeath": str(self.killDeath),
            "killsPerMinute": str(self.killsPerMinute),
            "headshots": str(self.headshots),
            "accuracy": str(self.accuracy),
            "revives": str(self.revives),
            "headShots": str(self.headShots),
            "longestHeadShot": str(self.longestHeadShot),
            "wins": str(self.wins),
            "highestKillStreak": str(self.highestKillStreak)
        }

    def __repr__(self):
        return f"PlayerStats(userName='{self.userName}', rank={self.rank}, ...)"


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
                 killsPerMinute: str, # 武器每分钟击杀数
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
        self.killsPerMinute = killsPerMinute
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
            killsPerMinute=str(data.get("killsPerMinute", "0.0")),
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
            "killsPerMinute": str(self.killsPerMinute),
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
                 killsPerMinute: str, # 载具每分钟击杀数
                 timeSpent: str, # 载具使用时间（小时）
                 type: str): # 载具类型
        self.name = name
        self.image = image
        self.kills = kills
        self.destroyed = destroyed
        self.killsPerMinute = killsPerMinute
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
            killsPerMinute=str(data.get("killsPerMinute", "0.0")),
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
            "killsPerMinute": str(self.killsPerMinute),
            "timeSpent": str(self.timeSpent),
            "type": str(self.type)
        }

    def __repr__(self):
        return f"Vehicle(name='{self.name}', kills={self.kills}, ...)"
