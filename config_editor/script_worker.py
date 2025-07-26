from PyQt6.QtCore import QThread, pyqtSignal

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

    def run(self):
        try:
            from module.script import Script
            self.script = Script(self.config_name)

            # 如果提供了日志窗口，开始日志捕获
            if self.log_window:
                self.log_window.start_log_capture()

            self.script.start()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            # 停止日志捕获
            if self.log_window:
                self.log_window.stop_log_capture()
            self.finished.emit()
