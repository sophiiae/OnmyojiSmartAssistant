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
            self.script = Script(self.config_name)

            # 如果提供了日志窗口，开始日志捕获
            if self.log_window:
                self.log_window.start_log_capture()

            logger.info(f"Starting script for config: {self.config_name}")

            # 直接启动脚本
            self.script.start()

        except Exception as e:
            if not self._stop_flag:
                self.error.emit(str(e))
        finally:
            # 停止日志捕获
            if self.log_window:
                self.log_window.stop_log_capture()
            self.finished.emit()
