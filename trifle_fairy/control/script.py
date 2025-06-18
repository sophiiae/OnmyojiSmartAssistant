from functools import cached_property
from datetime import datetime, timedelta
from multiprocessing import Queue
from pathlib import Path
import importlib
import importlib.util
from typing import Optional
import inflection
import sys

from module.base.logger import logger
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.control.server.adb_device import ADBDevice
from trifle_fairy.control.emulator import Emulator
from trifle_fairy.config.config import Config

class Script:
    def __init__(self, config: Config, device: ADBDevice) -> None:
        self.config = config
        self.device = device
        self.state_queue: Queue = Queue()  # Initialize Queue properly
        # Key: str, task name, value: int, failure count
        self.failure_record: dict[str, int] = {}  # Add type annotation
        self.is_running = False

    def run(self, name: str) -> bool:
        """

        :param name:  大写驼峰命名的任务名字
        :return:
        """
        if name == 'start' or name == 'goto_main':
            logger.error(f'Invalid task: `{name}`')
            return False

        try:
            self.device.get_screenshot()
            module_name = 'task_script'
            module_path = str(Path.cwd() / 'tasks' /
                              name / (module_name + '.py')
                              )
            logger.info(f'module_path: {
                        module_path}, module_name: {module_name}')
            task_module = self.load_module(module_name, module_path)
            task_module.TaskScript(
                config=self.config,
                device=self.device
            ).run()
            return True
        except TaskEnd:
            return True
        except Exception as e:
            logger.error(str(e))
            return False

    def start(self):
        logger.info(f'Start scheduler loop: {self.config.config_name}')
        self.is_running = True
        while 1:
            # Get task
            task = self.get_next_task()

            # Run
            logger.info(f'Scheduler: Start task ****{task}****')
            success = self.run(inflection.underscore(task))

            # Check failures
            # failed = deep_get(self.failure_record, keys=task, default=0)
            failed = self.failure_record[task] if task in self.failure_record else 0
            failed = 0 if success else failed + 1
            # deep_set(self.failure_record, keys=task, value=failed)
            self.failure_record[task] = failed
            if failed >= 3:
                logger.critical(f"Task `{task}` failed 3 or more times.")
                logger.critical("Possible reason #1: You haven't used it correctly. "
                                "Please read the help text of the options.")
                logger.critical("Possible reason #2: There is a problem with this task. "
                                "Please contact developers or try to fix it yourself.")
                logger.critical('Request human takeover')
                exit(1)

            if success:
                del self.config
                continue
            else:
                break

    def get_next_task(self) -> str:
        """
        Get the next task name in PascalCase format.
        Updates the current task and scheduler state.
        Returns the task name.
        """
        task = self.config.get_next()
        self.config.task = task

        # Update scheduler state if queue exists
        if self.state_queue:
            self.state_queue.put({
                "schedule": self.config.get_schedule_data()
            })

        logger.info(f"Next task: {task.name}")
        return task.name

    def load_module(self, moduleName: str, moduleFile: str):
        """
        Load a module from a file path
        :param moduleName: Name of the module
        :param moduleFile: File path with .py extension
        :return: The loaded module
        :raises: ImportError if module cannot be loaded
        """
        spec = importlib.util.spec_from_file_location(moduleName, moduleFile)
        if spec is None:
            raise ImportError(f"Could not load module from {moduleFile}")

        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            raise ImportError(f"Loader not found for {moduleFile}")
        spec.loader.exec_module(module)
        sys.modules[moduleName] = module
        return module


if __name__ == "__main__":
    emulator = Emulator(config_name="fairy")
    device = emulator.main_device
    script = Script(emulator.config, device)
    script.start()
