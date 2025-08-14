from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_checkbox_right_row, add_left_row

class GeneralBattleSection(QGroupBox):
    def __init__(self, config, section_name):
        super().__init__("战斗配置")
        self.config = config
        self.section_name = section_name
        self.battle_config = config[section_name]["general_battle_config"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 锁定队伍（只有CheckBox）
        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(
            self.battle_config["lock_team_enable"])
        add_left_row(layout, [self.lock_team_enable])

        # 预设设置（CheckBox+右侧控件）
        self.preset_enable = QCheckBox("启用预设")
        self.preset_enable.setChecked(self.battle_config["preset_enable"])
        self.preset_group = ValueButton()
        self.preset_group.setRange(1, 10)
        self.preset_group.setValue(self.battle_config["preset_group"])
        self.preset_team = ValueButton()
        self.preset_team.setRange(1, 10)
        self.preset_team.setValue(self.battle_config["preset_team"])
        add_checkbox_right_row(layout, self.preset_enable, [QLabel(
            "预设组:"), self.preset_group, QLabel("预设队伍:"), self.preset_team])

        # 绿色标记设置（CheckBox+右侧控件）
        self.green_enable = QCheckBox("启用绿色标记")
        self.green_enable.setChecked(self.battle_config["green_enable"])
        add_left_row(layout, [self.green_enable])

        # 绿标式神 （无CheckBox，左对齐）
        self.green_mark = SelectButton()
        self.green_mark.addItems(
            ["阴阳师", "第一个", "第二个", "第三个", "第四个", "第五个"])
        self.green_mark.setCurrentText(self.battle_config["green_mark"])
        add_left_row(layout, [QLabel("标记位置:(从左到右1-5)"), self.green_mark])

    def update_config(self):
        self.battle_config["lock_team_enable"] = self.lock_team_enable.isChecked()

        self.battle_config["preset_enable"] = self.preset_enable.isChecked()
        self.battle_config["preset_group"] = self.preset_group.value()
        self.battle_config["preset_team"] = self.preset_team.value()

        self.battle_config["green_enable"] = self.green_enable.isChecked()
        self.battle_config["green_mark"] = self.green_mark.currentText()
