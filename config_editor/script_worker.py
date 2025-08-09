from PyQt6.QtCore import QThread, pyqtSignal
from module.base.logger import logger

class ScriptWorker(QThread):
    """脚本运行工作线程"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log_signal = pyqtSignal(str)

    def __init__(self, config_name, log_window=None):
        super().__init__()
        self.config_name = config_name
        self.script = None
        self.log_window = log_window
        self._stop_flag = False

    def force_stop(self):
        """强制立即停止脚本"""
        self._stop_flag = True
        if self.script:
            # 立即停止脚本
            self.script.stop_immediately()

    def run(self):
        try:
            from module.script import Script
            from module.base.logger import set_current_config_name

            # 设置当前线程的配置名称，确保日志能正确过滤
            set_current_config_name(self.config_name)

            self.script = Script(self.config_name)

            # 如果提供了日志窗口，开始日志捕获
            if self.log_window:
                self.log_window.start_log_capture()

            logger.info(f"Starting script for config: {self.config_name}")

            # 直接启动脚本
            self.script.start()

        except Exception as e:
            if not self._stop_flag:
                logger.error(f"Script error: {str(e)}")
                self.error.emit(str(e))
            else:
                logger.info("脚本被用户终止")
        finally:
            # 记录脚本结束信息（在清除配置名称之前）
            if not self._stop_flag:
                logger.info("脚本运行完成")
            else:
                logger.info("脚本被用户终止")

            # 停止日志捕获
            if self.log_window:
                self.log_window.stop_log_capture()

            # 清除当前线程的配置名称
            from module.base.logger import clear_current_config_name
            clear_current_config_name()

            self.finished.emit()
