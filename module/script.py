
from functools import cached_property
from datetime import datetime, timedelta
from multiprocessing import Queue
from pathlib import Path
import importlib
import importlib.util
import sys
import json
import os

import inflection

from module.base.logger import logger, set_current_config_name, clear_current_config_name
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.control.server.device import Device
from module.config.config import Config


class Script:
    is_running = False
    _current_instance = None  # 添加全局变量跟踪当前实例

    def __init__(self, config_name: str = 'oas') -> None:
        self.config_name = config_name
        self.state_queue: Queue = Queue()
        # Key: str, task name, value: int, failure count
        self.failure_record = {}
        # 配置文件监控
        self.config_file_path = Path.cwd() / "configs" / f"{config_name}.json"
        self.last_config_mtime = self.get_config_mtime()
        # 强制重载配置的标志
        self._config_cache = None

    def get_config_mtime(self):
        """获取配置文件的修改时间"""
        try:
            if self.config_file_path.exists():
                return os.path.getmtime(self.config_file_path)
            return 0
        except OSError:
            return 0

    def check_config_file_changed(self):
        """检查配置文件是否发生变化"""
        current_mtime = self.get_config_mtime()
        if current_mtime != self.last_config_mtime:
            logger.info(f"配置文件 {self.config_name}.json 已更新，重新加载配置")
            self.last_config_mtime = current_mtime
            return True
        return False

    def force_reload_config(self):
        """强制重新加载配置"""
        # 清除缓存的config对象
        if hasattr(self, '_config_cache'):
            self._config_cache = None
        # 如果config属性已经被缓存，删除它以强制重新创建
        if 'config' in self.__dict__:
            del self.__dict__['config']
        logger.info(f"强制重新加载配置: {self.config_name}")

    @property
    def config(self) -> "Config":
        """动态配置属性，支持自动重载"""
        # 检查配置文件是否有变化
        if self.check_config_file_changed():
            self.force_reload_config()

        # 如果没有缓存的配置或需要重新加载，创建新的配置对象
        if self._config_cache is None:
            try:
                from module.config.config import Config
                self._config_cache = Config(config_name=self.config_name)
                logger.debug(f"创建新的配置对象: {self.config_name}")
            except RequestHumanTakeover:
                logger.critical('Request human takeover')
                self.is_running = False
                raise
            except Exception as e:
                logger.critical(str(e))
                self.is_running = False
                raise

        return self._config_cache

    @cached_property
    def device(self) -> "Device":
        try:
            from module.control.server.device import Device
            device = Device(config_name=self.config_name)
            return device
        except RequestHumanTakeover:
            logger.critical('Request human takeover')
            self.is_running = False
            raise
        except Exception as e:
            logger.critical(str(e))
            self.is_running = False
            raise

    def run(self, name: str) -> bool:
        """

        :param name:  大写驼峰命名的任务名字
        :return:
        """
        if name == 'start' or name == 'goto_main':
            logger.error(f'Invalid task: `{name}`')
            return False

        # 检查停止标志
        if not self.is_running:
            logger.info("Script stopped before running task")
            return False

        try:
            logger.info(f"开始执行任务: {name}")
            self.device.get_screenshot()
            module_name = 'task_script'
            module_path = str(Path.cwd() / 'tasks' /
                              name / (module_name + '.py')
                              )
            logger.info(
                f'module_path: {module_path}, module_name: {module_name}')

            task_module = self.load_module(module_name, module_path)
            task_module.TaskScript(
                device=self.device
            ).run()
        except TaskEnd:
            self.config.task_call(name)
        except Exception as e:
            logger.error(f"执行任务 {name} 时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
        return True

    def start(self):
        # 设置当前配置名称
        set_current_config_name(self.config_name)
        logger.info(f'Start scheduler loop: {self.config.model.config_name}')

        # 设置脚本为运行状态
        self.is_running = True
        # 设置当前实例为全局实例
        Script._current_instance = self

        try:
            while 1:
                # 检查停止标志
                if not self.is_running:
                    logger.info("Script stopped by user")
                    break

                # Get task
                task = self.get_next_task()

                # Run
                logger.info(f'Scheduler: Start task ****{task}****')
                success = self.run(inflection.underscore(task))

                # Check failures
                failed = self.failure_record[task] if task in self.failure_record else 0
                failed = 0 if success else failed + 1
                self.failure_record[task] = failed
                if failed >= 3:
                    logger.critical(f"Task `{task}` failed 3 or more times.")
                    logger.critical("Possible reason #1: You haven't used it correctly. "
                                    "Please read the help text of the options.")
                    logger.critical("Possible reason #2: There is a problem with this task. "
                                    "Please contact developers or try to fix it yourself.")
                    logger.critical('强制终止脚本')
                    # 不调用exit(1)，而是正常停止脚本
                    self.is_running = False
                    break

                if success:
                    self.is_running = True
                    # 不再手动删除config，让自动重载机制处理
                    continue
                else:
                    break
        finally:
            # 在清除配置名称之前记录脚本结束信息
            logger.info("脚本运行完成")
            # 清除当前配置名称
            clear_current_config_name()

    def get_next_task(self) -> str:
        """
        获取下一个任务的名字, 大驼峰。
        :return:
        """
        while True:
            task = self.config.get_next()

            # 检查任务是否到了执行时间
            now = datetime.now()
            if task.next_run > now:
                logger.info(f"Task {task.name} not ready yet, waiting...")
                # 等待一段时间后再次检查
                import time
                time.sleep(60)  # 等待60秒
                continue

            self.config.task = task

            # 将配置信息放入队列
            if self.state_queue:
                self.state_queue.put(
                    {"schedule": self.config.get_schedule_data()}
                )

            logger.info(
                f"Getting {task.name} and time: {datetime.strftime(task.next_run, '%Y-%m-%d %H:%M:%S')}")
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

    def gui_task_list(self) -> str:
        """
        获取给gui显示的任务列表
        :return:
        """
        result = {}
        for key, value in self.config.model.model_dump().items():
            if isinstance(value, str):
                continue
            if key == "restart":
                continue
            if "scheduler" not in value:
                continue

            scheduler = value["scheduler"]
            item = {"enable": scheduler["enable"],
                    "next_run": str(scheduler["next_run"])}
            key = self.config.model.type(key)
            result[key] = item
        return json.dumps(result)

    def reload_config_if_needed(self):
        """检查并重载配置（供外部调用）"""
        if self.check_config_file_changed():
            self.force_reload_config()
            return True
        return False

    def stop_immediately(self):
        """立即停止脚本"""
        self.is_running = False

        # 清理全局实例
        Script._current_instance = None

    @classmethod
    def get_current_instance(cls):
        """获取当前运行的脚本实例"""
        return cls._current_instance

    @classmethod
    def reload_current_config(cls):
        """重载当前运行脚本的配置"""
        instance = cls.get_current_instance()
        if instance:
            instance.force_reload_config()
            logger.info("通过全局方法重新加载了当前脚本的配置")
            return True
        else:
            logger.warning("没有正在运行的脚本实例，无法重载配置")
            return False


if __name__ == "__main__":
    script = Script("osa")
    print(script.gui_task_list())
    print(script.get_next_task())
