from trifle_fairy.config.config_model import ConfigModel
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Any

from module.base.logger import logger

DEFAULT_TIME = datetime(2024, 1, 1, 0, 0)

class Function:
    enable = False
    priority = 0

    def __init__(self, key: str, data: Dict[str, Any]):
        """
        Initialize a Function with configuration data
        :param key: The configuration key
        :param data: The configuration data dictionary
        """
        if not isinstance(data, dict):
            self.enable = False
            self.name = "Unknown"
            self.next_run = DEFAULT_TIME
            return

        self.setting = data

        self.enable: bool = data['enable']
        self.command: str = ConfigModel.type(key)
