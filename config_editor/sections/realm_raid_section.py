from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.switch_soul_section import SwitchSoulSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_left_row

class RealmRaidSection(QGroupBox):
    def __init__(self, config):
        super().__init__("结界突破设置")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "realm_raid")
        layout.addWidget(self.scheduler_section)

        # 突破配置
        raid_group = QGroupBox("突破配置")
        raid_layout = QVBoxLayout(raid_group)
        self.raid_config = self.config["realm_raid"]["raid_config"]

        # 开启寮突破（CheckBox独占一行）
        self.enable_guild_check = QCheckBox("开启寮突破")
        self.enable_guild_check.setChecked(
            self.raid_config['enable_guild_realm_raid'])
        add_left_row(raid_layout, [self.enable_guild_check])

        # 所需票数（无CheckBox，左对齐）
        self.tickets_required = ValueButton()
        self.tickets_required.setRange(0, 999)
        self.tickets_required.setValue(self.raid_config["tickets_required"])
        add_left_row(raid_layout, [QLabel("所需票数:"), self.tickets_required])

        # 攻击失败时（无CheckBox，左对齐）
        self.when_attack_fail = SelectButton()
        self.when_attack_fail.addItems(["Continue", "Exit"])
        self.when_attack_fail.setCurrentText(
            self.raid_config["when_attack_fail"])
        add_left_row(raid_layout, [QLabel("攻击失败时:"), self.when_attack_fail])

        layout.addWidget(raid_group)

        # 御魂切换设置
        self.switch_soul_section = SwitchSoulSection(self.config, "realm_raid")
        layout.addWidget(self.switch_soul_section)

        # # 添加通用战斗配置
        # self.general_battle_section = GeneralBattleSection(
        #     self.config, "realm_raid")
        # layout.addWidget(self.general_battle_section)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新突破配置
        self.raid_config["enable_guild_realm_raid"] = self.enable_guild_check.isChecked(
        )

        self.raid_config["tickets_required"] = self.tickets_required.value()
        self.raid_config["when_attack_fail"] = self.when_attack_fail.currentText()

        # 更新御魂切换配置
        self.switch_soul_section.update_config()

        # 更新通用战斗配置
        # self.general_battle_section.update_config()

    def refresh_from_config(self, config):
        """根据配置刷新UI控件"""
        try:
            # 更新内部配置引用
            self.config = config

            # 刷新调度器设置
            if hasattr(self.scheduler_section, 'refresh_from_config'):
                self.scheduler_section.refresh_from_config(config)

            # 重新获取配置引用
            realm_raid = config.get("realm_raid", {})
            self.raid_config = realm_raid.get("raid_config", {})

            # 刷新突破配置UI控件
            self.enable_guild_check.setChecked(
                self.raid_config.get("enable_guild_realm_raid", False))
            self.tickets_required.setValue(
                self.raid_config.get("tickets_required", 9))
            self.when_attack_fail.setCurrentText(
                self.raid_config.get("when_attack_fail", "Continue"))

        except Exception as e:
            from module.base.logger import logger
            logger.error(f"刷新结界突破设置UI时出错: {e}")
