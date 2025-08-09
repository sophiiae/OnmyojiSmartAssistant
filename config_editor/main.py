import json
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QTimer, QFileSystemWatcher
import os
import sys
from module.base.logger import logger

class ConfigTab(QWidget):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.config = self.load_config()
        self.is_running = False
        self.nav_buttons = {}

        # 文件监控器
        self.file_watcher = QFileSystemWatcher()
        # 规范化路径，确保路径格式一致
        self.normalized_path = os.path.abspath(config_path)
        self.file_watcher.addPath(self.normalized_path)
        self.file_watcher.fileChanged.connect(self.on_config_file_changed)
        logger.info(f"设置文件监控: {self.normalized_path}")

        # 防抖动定时器 - 避免文件频繁修改时多次触发
        self.reload_timer = QTimer(self)  # 设置父对象为self
        self.reload_timer.setSingleShot(True)
        self.reload_timer.timeout.connect(self.reload_config_from_file)

        # 记录最后修改时间，避免重复加载
        self.last_mtime = self.get_file_mtime()

    def get_file_mtime(self):
        """获取配置文件的修改时间"""
        try:
            return os.path.getmtime(self.config_path)
        except OSError:
            return 0

    def on_config_file_changed(self, path):
        """配置文件发生变化时的回调"""
        logger.info(f"配置文件变化信号触发: {path}")
        # 规范化接收到的路径进行比较
        normalized_received_path = os.path.abspath(path)
        logger.debug(
            f"规范化路径: {normalized_received_path} vs {self.normalized_path}")

        if normalized_received_path == self.normalized_path:
            logger.info(f"匹配的配置文件路径，直接调用重载")
            # 直接调用重载方法，不使用定时器
            self.reload_config_from_file()
        else:
            logger.debug(
                f"文件路径不匹配: {normalized_received_path} != {self.normalized_path}")

    def reload_config_from_file(self):
        """从文件重新加载配置"""
        logger.info(f"开始重新加载配置文件: {os.path.basename(self.config_path)}")
        try:
            current_mtime = self.get_file_mtime()
            logger.debug(f"当前修改时间: {current_mtime}, 上次修改时间: {self.last_mtime}")

            if current_mtime == self.last_mtime:
                # 文件没有实际修改，跳过
                logger.debug("文件修改时间未变化，跳过重载")
                return

            logger.info(
                f"检测到配置文件更改，重新加载: {os.path.basename(self.config_path)}")

            # 重新加载配置
            old_config = self.config.copy() if isinstance(
                self.config, dict) else self.config
            new_config = self.load_config()
            logger.debug(f"配置文件读取完成，比较配置差异")

            if new_config != self.config:
                logger.info("配置内容发生变化，更新UI")
                self.config = new_config
                self.last_mtime = current_mtime

                # 刷新UI
                self.update_nav_buttons()
                logger.info(f"配置界面已更新: {os.path.basename(self.config_path)}")
            else:
                logger.debug("配置内容未发生变化，跳过UI更新")

        except Exception as e:
            logger.error(f"重新加载配置文件时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            # 重新添加文件监控（某些情况下文件监控可能会失效）
            if not self.file_watcher.files():
                logger.warning("文件监控失效，重新添加监控")
                self.file_watcher.addPath(self.config_path)
            else:
                logger.debug("文件监控正常")

    def get_config_name(self):
        # 获取配置名称（文件名去掉.json后缀）
        config_name = os.path.splitext(
            os.path.basename(self.config_path))[0]
        return config_name

    def load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def update_nav_buttons(self):
        """更新导航按钮的状态样式"""
        # 启用的任务使用绿色
        enabled_style = """
            QPushButton {
                min-width: 80px;
                padding: 5px 10px;
                font-size: 12px;
                background-color: #ea698b;
                color: white;
            }
        """

        # 基础样式（默认样式）
        base_style = """
            QPushButton {
                min-width: 80px;
                padding: 5px 10px;
                font-size: 12px;
            }
        """

        for section_id, (btn, enable_path) in self.nav_buttons.items():
            if enable_path is None:
                # 没有启用状态的按钮使用基础样式
                btn.setStyleSheet(base_style)
                continue

            # 获取启用状态
            try:
                # 解析路径并获取值
                parts = enable_path.split('.')
                value = self.config
                for part in parts:
                    value = value[part]

                # 根据启用状态设置样式
                btn.setStyleSheet(enabled_style if value else base_style)
            except (KeyError, TypeError):
                # 如果路径无效，使用基础样式
                btn.setStyleSheet(base_style)


if __name__ == '__main__':
    # 延迟导入，避免循环导入问题
    from config_editor.config_editor import ConfigEditor

    app = QApplication(sys.argv)
    window = ConfigEditor()
    window.show()
    sys.exit(app.exec())
