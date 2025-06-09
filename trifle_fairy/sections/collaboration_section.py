from PyQt6.QtWidgets import (QVBoxLayout, QGroupBox, QCheckBox)

class CollaborationSection(QGroupBox):
    def __init__(self, config):
        super().__init__("协战奖励设置")
        self.config = config["collaboration"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加启用复选框
        self.enable_checkbox = QCheckBox("启用协战奖励")
        self.enable_checkbox.setChecked(self.config.get("enable", False))
        layout.addWidget(self.enable_checkbox)

        # 启用日常任务（CheckBox独占一行）
        self.enable_daily_routine = QCheckBox(
            "启用日常任务(按照日常任务设置执行)")
        self.enable_daily_routine.setChecked(
            self.config.get("enable_daily_routine", False))
        layout.addWidget(self.enable_daily_routine)

    def update_config(self):
        self.config["enable"] = self.enable_checkbox.isChecked()
        self.config["enable_daily_routine"] = self.enable_daily_routine.isChecked()
