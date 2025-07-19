from PyQt6.QtWidgets import (QCheckBox, QGroupBox, QVBoxLayout, QLabel)
from config_editor.widgets.value_button import ValueButton
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.utils import add_left_row

class ShikigamiActivitySection(QGroupBox):
    def __init__(self, config):
        super().__init__("式神活动设置")
        self.config = config

        # 确保所有必需的配置项存在
        if "shikigami_activity" not in self.config:
            self.config["shikigami_activity"] = {}
        shikigami_activity = self.config["shikigami_activity"]

        if "scheduler" not in shikigami_activity:
            shikigami_activity["scheduler"] = {
                "enable": False,
                "next_run": "2023-01-01 00:00:00",
                "priority": 5,
                "success_interval": "00:00:10:00",
                "failure_interval": "01:00:00:00"
            }

        if "climb_config" not in shikigami_activity:
            shikigami_activity["climb_config"] = {
                "enable_ap_mode": False,
                "auto_switch": False,
                "ticket_max": 50,
                "ap_max": 300,
                "lock_team_enable": True
            }

        if "general_battle_config" not in shikigami_activity:
            shikigami_activity["general_battle_config"] = {
                "lock_team_enable": True,
                "preset_enable": False,
                "preset_group": 1,
                "preset_team": 1,
                "green_enable": False,
                "green_mark": "不选择",
                "random_click_swipt_enable": False
            }

        if "switch_soul_config" not in shikigami_activity:
            shikigami_activity["switch_soul_config"] = {
                "enable": False,
                "switch_group_team": "-1,-1",
                "enable_switch_by_name": False,
                "group_name": "",
                "team_name": ""
            }

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

        # 更新通用战斗配置
        # self.general_battle_section.update_config()
