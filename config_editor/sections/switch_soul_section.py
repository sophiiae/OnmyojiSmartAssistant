from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.utils import add_checkbox_right_row, add_left_row
from config_editor.widgets.value_button import ValueButton

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

        # 切换组和队伍（无CheckBox，左对齐）
        self.switch_group_team = QLineEdit()
        self.switch_group_team.setText(
            self.switch_soul_config["switch_group_team"])

        add_checkbox_right_row(layout, self.switch_soul_enable, [QLabel(
            "切换组和队伍:"), self.switch_group_team])

        # # 按名称切换（只有CheckBox）
        # self.enable_switch_by_name = QCheckBox("按名称切换")
        # self.enable_switch_by_name.setChecked(
        #     self.switch_soul_config["enable_switch_by_name"])
        # add_left_row(layout, [self.enable_switch_by_name])

        # # 组名称（无CheckBox，左对齐）
        # self.group_name = QLineEdit()
        # self.group_name.setText(self.switch_soul_config["group_name"])
        # add_left_row(layout, [QLabel("组名称:"), self.group_name])

        # # 队伍名称（无CheckBox，左对齐）
        # self.team_name = QLineEdit()
        # self.team_name.setText(self.switch_soul_config["team_name"])
        # add_left_row(layout, [QLabel("队伍名称:"), self.team_name])

    def update_config(self):
        # 更新御魂切换配置
        self.switch_soul_config["enable"] = self.switch_soul_enable.isChecked()
        self.switch_soul_config["switch_group_team"] = self.switch_group_team.text(
        )

        # self.switch_soul_config["enable_switch_by_name"] = self.enable_switch_by_name.isChecked(
        # )
        # self.switch_soul_config["group_name"] = self.group_name.text()
        # self.switch_soul_config["team_name"] = self.team_name.text()
