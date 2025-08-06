from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_checkbox_right_row, add_left_row

class RoyalBattleSection(QGroupBox):
    def __init__(self, config, section_name):
        super().__init__("斗技配置")
        self.config = config
        self.section_name = section_name
        self.royal_battle_config = config[section_name]["royal_battle_config"]
        self.switch_soul_config = config[section_name]["switch_soul_config"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(
            self.config, self.section_name)
        layout.addWidget(self.scheduler_section)

        # 斗技配置
        royal_battle_group = QGroupBox("斗技配置")
        royal_battle_layout = QVBoxLayout(royal_battle_group)

        # 上名士（只有CheckBox）
        self.elite_enable = QCheckBox("上名士")
        self.elite_enable.setChecked(self.royal_battle_config["elite"])
        add_left_row(royal_battle_layout, [self.elite_enable])

        # 段位（无CheckBox，左对齐）
        self.rank = SelectButton()
        self.rank.addItems(
            ["一段", "二段", "三段", "四段", "五段", "六段", "七段", "八段", "九段"])
        self.rank.setCurrentText(self.royal_battle_config["rank"])
        add_left_row(royal_battle_layout, [QLabel("段位:"), self.rank])

        # 打满荣誉积分（只有CheckBox）
        self.full_honor_points_enable = QCheckBox("打满荣誉积分")
        self.full_honor_points_enable.setChecked(
            self.royal_battle_config["full_honor_points"])
        add_left_row(royal_battle_layout, [self.full_honor_points_enable])

        # 阴阳师选择（无CheckBox，左对齐）
        self.onmyoji = SelectButton()
        self.onmyoji.addItems(["自动", "晴明", "源博雅", "神乐", "八百比丘尼", "源赖光"])
        self.onmyoji.setCurrentText(self.royal_battle_config["onmyoji"])
        add_left_row(royal_battle_layout, [QLabel("阴阳师:"), self.onmyoji])

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

        royal_battle_layout.addWidget(switch_soul_group)
        layout.addWidget(royal_battle_group)

    def update_config(self):
        # 更新调度配置
        self.scheduler_section.update_config()

        self.royal_battle_config["elite"] = self.elite_enable.isChecked()
        self.royal_battle_config["rank"] = self.rank.currentText()
        self.royal_battle_config["onmyoji"] = self.onmyoji.currentText()
        self.royal_battle_config["full_honor_points"] = self.full_honor_points_enable.isChecked(
        )
        # 更新御魂切换配置
        self.switch_soul_config["enable"] = self.switch_soul_enable.isChecked()
        self.switch_soul_config["switch_group_team"] = self.switch_group_team.text(
        )
