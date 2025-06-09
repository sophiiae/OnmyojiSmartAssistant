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
        self.config = config["area_boss"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加启用复选框
        self.enable_checkbox = QCheckBox("启用地域鬼王")
        self.enable_checkbox.setChecked(self.config.get("enable", False))
        layout.addWidget(self.enable_checkbox)

        # 鬼王数量（无CheckBox，左对齐）
        self.boss_number_spin = ValueButton()
        self.boss_number_spin.setRange(0, 9999)
        self.boss_number_spin.setValue(self.config.get("boss_number", 0))
        add_left_row(layout, [QLabel("鬼王数量"), self.boss_number_spin])

        # 领取奖励（CheckBox独占一行）
        self.boss_reward = QCheckBox("领取奖励")
        self.boss_reward.setChecked(self.config["boss_reward"])
        add_left_row(layout, [self.boss_reward])

    def update_config(self):
        self.config["enable"] = self.enable_checkbox.isChecked()
        # 更新鬼王配置
        self.config["boss_number"] = self.boss_number_spin.value()
        self.config["boss_reward"] = self.boss_reward.isChecked()
