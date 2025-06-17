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
        if not isinstance(data, dict) or 'enable' not in data:
            self.enable = False
            self.name = "Unknown"
            self.next_run = DEFAULT_TIME
            return

        self.setting = data
        self.enable: bool = data['enable']
        self.name: str = ConfigModel.type(key)
        self.next_run: datetime = datetime.now()

        priority = data['priority']
        if isinstance(priority, str):
            priority = int(priority)
        self.priority: int = priority
        if not isinstance(self.priority, int):
            logger.error(f"Invalid priority: {self.priority}")

    def __str__(self):
        enable = "Enable" if self.enable else "Disable"
        return f"{self.name} ({enable}, {self.priority}, {str(self.next_run)})"

    __repr__ = __str__

    def __eq__(self, other):
        if not isinstance(other, Function):
            return False

        if self.name == other.name and self.next_run == other.next_run:
            return True
        else:
            return False
