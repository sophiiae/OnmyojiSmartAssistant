from PyQt6.QtWidgets import (
    QCheckBox, QGroupBox, QVBoxLayout, QLabel, QLineEdit)
from config_editor.widgets.value_button import ValueButton
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.utils import add_left_row

class ShikigamiActivitySection(QGroupBox):
    def __init__(self, config):
        super().__init__("式神活动设置")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        climb_config = self.config["shikigami_activity"]["climb_config"]

        # 添加调度设置
        self.scheduler_section = SchedulerSection(
            self.config, "shikigami_activity")
        layout.addWidget(self.scheduler_section)

        # 爬塔配置
        climb_group = QGroupBox("爬塔配置")
        climb_layout = QVBoxLayout(climb_group)

        # 启用体力模式（CheckBox独占一行）
        self.enable_ap_mode = QCheckBox("启用体力模式")
        self.enable_ap_mode.setChecked(
            climb_config.get("enable_ap_mode", False))
        add_left_row(climb_layout, [self.enable_ap_mode])

        # 自动切换（CheckBox独占一行）
        self.auto_switch = QCheckBox("自动切换")
        self.auto_switch.setChecked(climb_config.get("auto_switch", False))
        add_left_row(climb_layout, [self.auto_switch])

        # 最大票数（无CheckBox，左对齐）
        self.max_tickets_spin = ValueButton()
        self.max_tickets_spin.setRange(0, 9999)
        self.max_tickets_spin.setValue(climb_config.get("ticket_max", 50))
        add_left_row(climb_layout, [QLabel("最大票数"), self.max_tickets_spin])

        # 最大体力（无CheckBox，左对齐）
        self.max_stamina_spin = ValueButton()
        self.max_stamina_spin.setRange(0, 9999)
        self.max_stamina_spin.setValue(climb_config.get("ap_max", 300))
        add_left_row(climb_layout, [QLabel("最大体力"), self.max_stamina_spin])

        # 锁定队伍（CheckBox独占一行）
        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(
            climb_config.get("lock_team_enable", True))
        add_left_row(climb_layout, [self.lock_team_enable])

        layout.addWidget(climb_group)

        # 御魂切换设置
        switch_soul_group = QGroupBox("御魂切换设置")
        switch_soul_layout = QVBoxLayout(switch_soul_group)
        self.switch_soul_config = self.config["shikigami_activity"]["switch_soul_config"]

        # 启用御魂切换（只有CheckBox）
        self.switch_soul_enable = QCheckBox("启用御魂切换")
        self.switch_soul_enable.setChecked(self.switch_soul_config["enable"])
        add_left_row(switch_soul_layout, [self.switch_soul_enable])

        # 切换组和队伍（无CheckBox，左对齐）
        self.switch_group_team = QLineEdit()
        self.switch_group_team.setText(
            self.switch_soul_config["switch_group_team"])
        add_left_row(switch_soul_layout, [QLabel(
            "切换组和队伍"), self.switch_group_team])

        layout.addWidget(switch_soul_group)

        # # 添加通用战斗配置
        # self.general_battle_section = GeneralBattleSection(
        #     self.config, "shikigami_activity")
        # layout.addWidget(self.general_battle_section)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新爬塔配置
        climb_config = self.config["shikigami_activity"]["climb_config"]
        climb_config["enable_ap_mode"] = self.enable_ap_mode.isChecked()
        climb_config["auto_switch"] = self.auto_switch.isChecked()
        climb_config["ticket_max"] = self.max_tickets_spin.value()
        climb_config["ap_max"] = self.max_stamina_spin.value()
        climb_config["lock_team_enable"] = self.lock_team_enable.isChecked()

        # 更新御魂切换配置
        self.switch_soul_config["enable"] = self.switch_soul_enable.isChecked()
        self.switch_soul_config["switch_group_team"] = self.switch_group_team.text(
        )

        # 更新通用战斗配置
        # self.general_battle_section.update_config()
