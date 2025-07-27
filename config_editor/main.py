import json
from PyQt6.QtWidgets import QWidget
import os
class ConfigTab(QWidget):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.config = self.load_config()
        self.is_running = False
        self.nav_buttons = {}

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
                background-color: #4CAF50;
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
