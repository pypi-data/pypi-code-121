from typing import List
from pydantic import BaseModel
from graia.ariadne.model import MiraiSession
from pathlib import Path
from loguru import logger
import json


class BotConfig(BaseModel):
    master: int = 0
    admins: List[int] = []
    nickname: List[str] = ["LBot"]


class DataBaseConfig(BaseModel):
    url: str = "mongodb://localhost:27017"


class AwordaConfig(BaseModel):
    mirai: MiraiSession = MiraiSession(
        host="http://localhost:8080",
        verify_key="",
        account=123456789,
    )
    bot: BotConfig = BotConfig()
    db: DataBaseConfig = DataBaseConfig()

    @classmethod
    def from_json_file(cls, path: str = "config.json"):
        """
        从 json 文件中读取配置
        @param path: 配置文件路径
        """
        _path = Path(path)
        if not _path.exists():
            logger.warning(f"配置文件 {path} 不存在,按任意键生成默认配置文件, Crtl-C 取消")
            input()
            cls().generate_default_config_file(path)

        with open(path, "r", encoding="utf-8") as f:
            return cls.parse_obj(json.load(f))

    def generate_default_config_file(self, path: str = "config.json"):
        """
        生成默认配置文件
        @param path: 配置文件路径
        """
        _path = Path(path)
        if _path.exists():
            logger.warning(f"配置文件 {path} 已存在!按任意键覆盖, Crtl-C 取消")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.dict(), f, ensure_ascii=False, indent=4)
