from PyQt6.QtWidgets import (QCheckBox, QComboBox, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QLabel)
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.general_battle_section import GeneralBattleSection

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

class ShikigamiActivitySection(QGroupBox):
    def __init__(self, config):
        super().__init__("式神活动设置")
        self.config = config["shikigami_activity"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加启用复选框
        self.enable_checkbox = QCheckBox("启用式神活动")
        self.enable_checkbox.setChecked(self.config.get("enable", False))
        layout.addWidget(self.enable_checkbox)

        # 启用体力模式（CheckBox独占一行）
        self.enable_ap_mode = QCheckBox("启用体力模式")
        self.enable_ap_mode.setChecked(
            self.config.get("enable_ap_mode", False))
        add_left_row(layout, [self.enable_ap_mode])

        # 自动切换（CheckBox独占一行）
        self.auto_switch = QCheckBox("自动切换")
        self.auto_switch.setChecked(self.config.get("auto_switch", False))
        add_left_row(layout, [self.auto_switch])

        # 最大票数（无CheckBox，左对齐）
        self.max_tickets_spin = ValueButton()
        self.max_tickets_spin.setRange(0, 9999)
        self.max_tickets_spin.setValue(self.config.get("ticket_max", 50))
        add_left_row(layout, [QLabel("最大票数"), self.max_tickets_spin])

        # 最大体力（无CheckBox，左对齐）
        self.max_stamina_spin = ValueButton()
        self.max_stamina_spin.setRange(0, 9999)
        self.max_stamina_spin.setValue(self.config.get("ap_max", 300))
        add_left_row(layout, [QLabel("最大体力"), self.max_stamina_spin])

        # 锁定队伍（CheckBox独占一行）
        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(
            self.config.get("lock_team_enable", True))
        add_left_row(layout, [self.lock_team_enable])

    def update_config(self):
        self.config["enable"] = self.enable_checkbox.isChecked()
        # 更新爬塔配置
        self.config["enable_ap_mode"] = self.enable_ap_mode.isChecked()
        self.config["auto_switch"] = self.auto_switch.isChecked()
        self.config["ticket_max"] = self.max_tickets_spin.value()
        self.config["ap_max"] = self.max_stamina_spin.value()
        self.config["lock_team_enable"] = self.lock_team_enable.isChecked()
