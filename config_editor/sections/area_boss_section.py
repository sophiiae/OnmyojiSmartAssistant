from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QComboBox, QGroupBox)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.general_battle_section import GeneralBattleSection
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

class AreaBossSection(QGroupBox):
    def __init__(self, config):
        super().__init__("地域鬼王设置")
        self.config = config

        # 确保所有必需的配置项存在
        if "area_boss" not in self.config:
            self.config["area_boss"] = {}
        area_boss = self.config["area_boss"]

        if "scheduler" not in area_boss:
            area_boss["scheduler"] = {
                "enable": False,
                "next_run": "2023-01-01 00:00:00",
                "priority": 5,
                "success_interval": "00:00:30:00",
                "failure_interval": "00:00:10:00"
            }

        if "boss" not in area_boss:
            area_boss["boss"] = {
                "boss_number": 0,
                "boss_reward": True,
                "reward_floor": "一星",
                "use_collect": False,
                "Attack_60": False
            }

        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "area_boss")
        layout.addWidget(self.scheduler_section)

        # 鬼王配置
        boss_group = QGroupBox("鬼王配置")
        boss_layout = QVBoxLayout(boss_group)
        self.boss_config = self.config["area_boss"]["boss"]

        # 鬼王数量（无CheckBox，左对齐）
        self.boss_number_spin = ValueButton()
        self.boss_number_spin.setRange(0, 9999)
        self.boss_number_spin.setValue(self.boss_config.get("boss_number", 0))
        add_left_row(boss_layout, [QLabel("鬼王数量"), self.boss_number_spin])

        # 领取奖励（CheckBox独占一行）
        self.boss_reward = QCheckBox("领取奖励")
        self.boss_reward.setChecked(self.boss_config["boss_reward"])
        add_left_row(boss_layout, [self.boss_reward])

        # 奖励星级（无CheckBox，左对齐）
        self.reward_floor = SelectButton()
        self.reward_floor.addItems(["一星", "二星", "三星"])
        self.reward_floor.setCurrentText(self.boss_config["reward_floor"])
        add_left_row(boss_layout, [QLabel("奖励星级:"), self.reward_floor])

        # 使用集结（CheckBox独占一行）
        self.use_collect = QCheckBox("使用集结")
        self.use_collect.setChecked(self.boss_config["use_collect"])
        add_left_row(boss_layout, [self.use_collect])

        # 60秒攻击（CheckBox独占一行）
        self.Attack_60 = QCheckBox("60秒攻击")
        self.Attack_60.setChecked(self.boss_config["Attack_60"])
        add_left_row(boss_layout, [self.Attack_60])

        layout.addWidget(boss_group)

        # 添加通用战斗配置
        self.general_battle_section = GeneralBattleSection(
            self.config, "area_boss")
        layout.addWidget(self.general_battle_section)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新鬼王配置
        self.boss_config["boss_number"] = self.boss_number_spin.value()
        self.boss_config["boss_reward"] = self.boss_reward.isChecked()
        self.boss_config["reward_floor"] = self.reward_floor.currentText()
        self.boss_config["use_collect"] = self.use_collect.isChecked()
        self.boss_config["Attack_60"] = self.Attack_60.isChecked()

        # 更新通用战斗配置
        self.general_battle_section.update_config()
