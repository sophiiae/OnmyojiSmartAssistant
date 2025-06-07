from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QComboBox, QGroupBox, QLineEdit)
from PyQt6.QtCore import Qt
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton

def add_checkbox_right_row(layout, checkbox, right_widgets):
    row = QHBoxLayout()
    row.addWidget(checkbox)
    row.addStretch()
    for w in right_widgets:
        row.addWidget(w)
    layout.addLayout(row)

def add_left_row(layout, widgets):
    row = QHBoxLayout()
    for w in widgets:
        row.addWidget(w)
    layout.addLayout(row)

class GeneralBattleSection(QGroupBox):
    def __init__(self, config, section_name):
        super().__init__("战斗配置")
        self.config = config
        self.section_name = section_name
        self.battle_config = config[section_name]["general_battle_config"]
        self.switch_soul_config = config[section_name]["switch_soul_config"]
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
        self.green_mark = SelectButton()
        self.green_mark.addItems(
            ["不选择", "选择第一个", "选择第二个", "选择第三个", "选择第四个", "选择第五个"])
        mark_map = {"不选择": 0, "选择第一个": 1, "选择第二个": 2,
                    "选择第三个": 3, "选择第四个": 4, "选择第五个": 5}
        self.green_mark.setCurrentIndex(
            mark_map.get(self.battle_config["green_mark"], 0))
        add_checkbox_right_row(layout, self.green_enable, [
                               QLabel("标记位置:(从左到右1-5)"), self.green_mark])

        # 随机点击滑动（只有CheckBox）
        self.random_click_swipt_enable = QCheckBox("启用随机点击滑动")
        self.random_click_swipt_enable.setChecked(
            self.battle_config["random_click_swipt_enable"])
        add_left_row(layout, [self.random_click_swipt_enable])

        # 御魂切换设置
        switch_soul_group = QGroupBox("御魂切换设置")
        switch_soul_layout = QVBoxLayout(switch_soul_group)

        # 启用御魂切换（只有CheckBox）
        self.switch_soul_enable = QCheckBox("启用御魂切换")
        self.switch_soul_enable.setChecked(self.switch_soul_config["enable"])
        add_left_row(switch_soul_layout, [self.switch_soul_enable])

        # 切换组和队伍（无CheckBox，左对齐）
        self.switch_group_team = QLineEdit()
        self.switch_group_team.setText(
            self.switch_soul_config["switch_group_team"])
        add_left_row(switch_soul_layout, [QLabel(
            "切换组和队伍:"), self.switch_group_team])

        # 按名称切换（只有CheckBox）
        self.enable_switch_by_name = QCheckBox("按名称切换")
        self.enable_switch_by_name.setChecked(
            self.switch_soul_config["enable_switch_by_name"])
        add_left_row(switch_soul_layout, [self.enable_switch_by_name])

        # 组名称（无CheckBox，左对齐）
        self.group_name = QLineEdit()
        self.group_name.setText(self.switch_soul_config["group_name"])
        add_left_row(switch_soul_layout, [QLabel("组名称:"), self.group_name])

        # 队伍名称（无CheckBox，左对齐）
        self.team_name = QLineEdit()
        self.team_name.setText(self.switch_soul_config["team_name"])
        add_left_row(switch_soul_layout, [QLabel("队伍名称:"), self.team_name])

        layout.addWidget(switch_soul_group)

    def update_config(self):
        self.battle_config["lock_team_enable"] = self.lock_team_enable.isChecked()
        self.battle_config["preset_enable"] = self.preset_enable.isChecked()
        self.battle_config["preset_group"] = self.preset_group.value()
        self.battle_config["preset_team"] = self.preset_team.value()
        self.battle_config["green_enable"] = self.green_enable.isChecked()
        mark_map = {0: "不选择", 1: "选择第一个", 2: "选择第二个",
                    3: "选择第三个", 4: "选择第四个", 5: "选择第五个"}
        self.battle_config["green_mark"] = mark_map[self.green_mark.currentIndex()]
        self.battle_config["random_click_swipt_enable"] = self.random_click_swipt_enable.isChecked(
        )

        # 更新御魂切换配置
        self.switch_soul_config["enable"] = self.switch_soul_enable.isChecked()
        self.switch_soul_config["switch_group_team"] = self.switch_group_team.text(
        )
        self.switch_soul_config["enable_switch_by_name"] = self.enable_switch_by_name.isChecked(
        )
        self.switch_soul_config["group_name"] = self.group_name.text()
        self.switch_soul_config["team_name"] = self.team_name.text()
