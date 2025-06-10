from typing import Optional
import copy

from trifle_fairy.config.function import Function
from trifle_fairy.config.config_model import ConfigModel
from module.base.logger import logger
from module.base.exception import RequestHumanTakeover

class Config:
    def __init__(self, config_name: str):
        self.config_name = config_name
        self.waiting_tasks: list["Function"] = []
        self.task: Optional["Function"] = None  # 任务名大驼峰
        self.model = ConfigModel(config_name=config_name)

    def get_next(self) -> Function:
        """
        获取下一个要执行的任务
        :return:
        """

        # 哪怕是没有任务，也要返回一个任务，这样才能保证调度器正常运行
        if self.waiting_tasks:
            logger.info("No task pending")
            task = copy.deepcopy(self.waiting_tasks[0])
            logger.info(f"Waiting Task: {task.name}")
            return task
        else:
            logger.critical("No task waiting or pending")
            logger.critical("Please enable at least one task")
            raise RequestHumanTakeover

    def get_schedule_data(self) -> dict[str, dict]:
        """
        获取调度器的数据， 但是你必须使用update_scheduler来更新信息
        :return:
        """
        running = {}
        if self.task is not None:
            running = {"name": self.task.name}

        waiting = []
        for w in self.waiting_tasks:
            item = {"name": w.name}
            waiting.append(item)

        data = {"running": running, "waiting": waiting}
        return data
