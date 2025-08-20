
from functools import cached_property
from datetime import datetime
from multiprocessing import Queue
from pathlib import Path
import importlib
import importlib.util
import sys
import json
import os
import time
import math
import inflection

from module.base.logger import logger, set_current_config_name, clear_current_config_name
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.base.exception_handler import ExceptionHandler
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
            # 设置当前执行的任务
            self._current_task = name

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
            return True

        except Exception as e:
            if isinstance(e, TaskEnd):
                # 如果没有异常，任务成功完成
                logger.info(f"任务 {name} 执行成功")
                # 清除当前任务记录
                self._current_task = None
                return True

            # 记录详细的异常信息
            import traceback
            logger.error(f"任务 {name} 执行时发生异常: {str(e)}")
            logger.error(f"异常类型: {type(e).__name__}")
            logger.error(f"配置文件: {self.config_name}.json")
            logger.error(f"异常堆栈:\n{traceback.format_exc()}")

            # 使用异常处理器来处理异常
            handler_result = ExceptionHandler.handle_task_exception(e, name)

            # 根据处理结果决定是否继续
            if handler_result["should_continue"]:
                logger.info("OSA将继续运行，处理下一个任务")
            else:
                logger.critical("OSA将停止运行，需要人工干预")
                logger.critical(f"配置文件: {self.config_name}.json")
                self.is_running = False

            # 清除当前任务记录
            self._current_task = None

            # 返回任务是否成功
            return handler_result.get("handled", False)

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
                logger.info(f'任务调度器: 开始执行任务 {task}')
                success = self.run(inflection.underscore(task))

                # Check failures
                failed = self.failure_record[task] if task in self.failure_record else 0
                failed = 0 if success else failed + 1
                self.failure_record[task] = failed
                if failed >= 3:
                    logger.critical(f"任务 `{task}` 连续失败3次或以上")
                    logger.critical(f"失败记录: {self.failure_record}")
                    logger.critical(f"配置文件: {self.config_name}.json")
                    logger.critical("可能的原因 #1: 配置使用不当，请检查相关选项的说明")
                    logger.critical("可能的原因 #2: 任务本身存在问题，请联系开发者或尝试自行修复")
                    logger.critical(
                        f"强制终止脚本 - 失败任务: {task} - 配置文件: {self.config_name}")
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
                # 计算需要等待的时间
                wait_time = task.next_run - now
                wait_seconds = wait_time.total_seconds()
                logger.info(
                    f"Next run time: {datetime.strftime(task.next_run, '%Y-%m-%d %H:%M:%S')}")

                # 运行等待任务
                try:
                    logger.info(
                        f"⏳ Task {task.name} not ready yet, waiting {wait_seconds:.0f} seconds...")
                    wait_minutes = math.ceil(wait_seconds / 60)
                    self.run_waiting_task(wait_minutes)
                except Exception as e:
                    logger.error(f"等待任务执行出错: {e}")
                    # 如果等待任务出错，继续等待
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

    def run_waiting_task(self, wait_minutes: float):
        """
        运行等待任务
        :param wait_seconds: 需要等待的秒数
        """
        try:
            # 加载等待任务模块
            module_name = 'waiting_task'
            module_path = str(Path.cwd() / 'tasks' / (module_name + '.py'))

            task_module = self.load_module(module_name, module_path)

            # 创建等待任务实例并运行
            waiting_task = task_module.WaitingTask(device=self.device)

            # 将秒数转换为分钟，使用ceil向上取整
            logger.info(f"⏳ 等待时间: -> {wait_minutes}分钟")

            # 调用等待任务的run方法，传入分钟数
            waiting_task.run(wait_minutes)

        except Exception as e:
            logger.error(f"加载或运行等待任务时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

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
        logger.critical(f"脚本被强制停止 - 配置文件: {self.config_name}.json")
        logger.critical(f"当前失败记录: {self.failure_record}")

        # 记录当前正在执行的任务（如果有的话）
        try:
            current_task = getattr(self, '_current_task', None)
            if current_task:
                logger.critical(f"正在执行的任务: {current_task}")
        except:
            pass

        # 记录配置文件路径
        config_file_path = Path.cwd() / "configs" / f"{self.config_name}.json"
        if config_file_path.exists():
            logger.critical(f"配置文件路径: {config_file_path}")
        else:
            logger.critical(f"配置文件不存在: {config_file_path}")

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
