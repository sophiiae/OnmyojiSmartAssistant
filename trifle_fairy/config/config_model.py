import json
import os
import re

from pathlib import Path
from pydantic import BaseModel, Field
from module.control.config.enums import *
from trifle_fairy.config.config_base import *
from module.base.logger import logger
from module.base.exception import RequestHumanTakeover

class ConfigModel(BaseModel):
    config_name: str = Field(default="fairy")
    script: ScriptSetting = Field(default_factory=ScriptSetting)
    daily_routine: DailyRoutine = Field(
        default_factory=DailyRoutine)
    wanted_quests: WantedQuests = Field(
        default_factory=WantedQuests)
    collaboration: Collaboration = Field(
        default_factory=Collaboration)
    royal_battle: RoyalBattle = Field(
        default_factory=RoyalBattle)
    exploration: Exploration = Field(
        default_factory=Exploration)
    area_boss: AreaBoss = Field(default_factory=AreaBoss)
    goryou_realm: Goryou = Field(
        default_factory=Goryou)
    shikigami_activity: ShikigamiActivity = Field(
        default_factory=ShikigamiActivity)
    summon: Summon = Field(
        default_factory=Summon)

    def __init__(self):
        data = self.read_json()
        data["config_name"] = 'fairy'
        super().__init__(**data)

    @staticmethod
    def read_json() -> dict:
        """
        :param config_name:  no ext
        :return: dict
        """
        file = Path.cwd() / "trifle_fairy" / f"fairy.json"

        if not os.path.exists(file):
            return {}

        with open(file, encoding='utf-8') as f:
            data = json.load(f)
            return data

    @staticmethod
    def type(key: str) -> str:
        """
        输入模型的键值，获取这个字段对象的类型 比如输入是orochi输出是Orochi
        :param key:
        :return:
        """
        field_type: str = str(ConfigModel.__annotations__[key])
        # return field_type
        if '.' in field_type:
            classname = field_type.split('.')[-1][:-2]
            return classname
        else:
            classname = re.findall(r"'([^']*)'", field_type)[0]
            return classname

    @staticmethod
    def deep_get(obj, keys: str | list[str], default=None):
        """
        递归获取模型的值
        :param obj:
        :param keys:
        :param default:
        :return:
        """
        if not isinstance(keys, list):
            keys = keys.split('.')
        value = obj
        try:
            for key in keys:
                value = getattr(value, key)
        except AttributeError:
            return default
        return value
