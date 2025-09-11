from PyQt6.QtWidgets import (
    QCheckBox, QGroupBox, QVBoxLayout, QLabel, QGridLayout)
from config_editor.widgets.value_button import ValueButton
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.switch_soul_section import SwitchSoulSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.utils import add_left_row

class ShikigamiActivitySection(QGroupBox):
    name = "shikigami_activity"

    def __init__(self, config):
        super().__init__("式神活动")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        climb_config = self.config[self.name]["climb_config"]

        # 添加调度设置
        self.scheduler_section = SchedulerSection(
            self.config, self.name)
        layout.addWidget(self.scheduler_section)

        # 爬塔配置
        climb_group = QGroupBox("爬塔配置")
        climb_layout = QVBoxLayout(climb_group)

        grid = QGridLayout()

        # 启用体力模式（CheckBox独占一行）
        self.enable_ap_mode = QCheckBox("启用体力模式")
        self.enable_ap_mode.setChecked(
            climb_config.get("enable_ap_mode", False))
        grid.addWidget(self.enable_ap_mode, 0, 0)

        # 自动切换（CheckBox独占一行）
        self.auto_switch = QCheckBox("自动切换")
        self.auto_switch.setChecked(climb_config.get("auto_switch", False))
        grid.addWidget(self.auto_switch, 0, 1)

        # 启用周年庆模式（CheckBox独占一行）
        self.anniversary_mode = QCheckBox("启用周年庆模式")
        self.anniversary_mode.setChecked(
            climb_config.get("anniversary_mode", False))
        grid.addWidget(self.anniversary_mode, 1, 0)

        # 启用超鬼王模式（CheckBox独占一行）
        self.demon_king_mode = QCheckBox("启用超鬼王模式")
        self.demon_king_mode.setChecked(
            climb_config.get("demon_king_mode", False))
        grid.addWidget(self.demon_king_mode, 1, 1)

        group = QGroupBox("活动模式设置")
        group.setLayout(grid)
        climb_layout.addWidget(group)

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

        layout.addWidget(climb_group)

        # 御魂切换设置
        self.switch_soul_section = SwitchSoulSection(
            self.config, self.name)
        layout.addWidget(self.switch_soul_section)

        # 添加通用战斗配置
        self.general_battle_section = GeneralBattleSection(
            self.config, self.name)
        layout.addWidget(self.general_battle_section)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新爬塔配置
        climb_config = self.config[self.name]["climb_config"]
        climb_config["enable_ap_mode"] = self.enable_ap_mode.isChecked()
        climb_config["anniversary_mode"] = self.anniversary_mode.isChecked()
        climb_config["demon_king_mode"] = self.demon_king_mode.isChecked()
        climb_config["auto_switch"] = self.auto_switch.isChecked()
        climb_config["ticket_max"] = self.max_tickets_spin.value()
        climb_config["ap_max"] = self.max_stamina_spin.value()

        # 更新御魂切换配置
        self.switch_soul_section.update_config()

        # 更新通用战斗配置
        self.general_battle_section.update_config()

    def refresh_from_config(self, config):
        """根据配置刷新UI控件"""
        try:
            # 更新内部配置引用
            self.config = config

            # 刷新调度器设置
            if hasattr(self.scheduler_section, 'refresh_from_config'):
                self.scheduler_section.refresh_from_config(config)

        except Exception as e:
            from module.base.logger import logger
            logger.error(f"刷新式神活动设置UI时出错: {e}")
