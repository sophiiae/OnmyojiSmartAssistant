from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.utils import add_left_row

class SwitchSoulSection(QGroupBox):
    def __init__(self, config, task_name):
        super().__init__("御魂切换设置")
        self.config = config
        self.task_name = task_name
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        self.switch_soul_config = self.config[self.task_name]["switch_soul_config"]

        # 启用御魂切换（只有CheckBox）
        self.switch_soul_enable = QCheckBox("启用御魂切换")
        self.switch_soul_enable.setChecked(self.switch_soul_config["enable"])
        add_left_row(layout, [self.switch_soul_enable])

        # 切换组和队伍（无CheckBox，左对齐）
        self.switch_group_team = QLineEdit()
        self.switch_group_team.setText(
            self.switch_soul_config["switch_group_team"])
        add_left_row(layout, [QLabel(
            "切换组和队伍"), self.switch_group_team])

    def update_config(self):
        # 更新御魂切换配置
        self.switch_soul_config["enable"] = self.switch_soul_enable.isChecked()
        self.switch_soul_config["switch_group_team"] = self.switch_group_team.text(
        )
