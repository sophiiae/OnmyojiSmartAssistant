from PyQt6.QtCore import QThread, pyqtSignal

class ScriptWorker(QThread):
    """脚本运行工作线程"""
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, config_name):
        super().__init__()
        self.config_name = config_name
        self.script = None

    def run(self):
        try:
            from module.script import Script
            self.script = Script(self.config_name)
            self.script.start()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
