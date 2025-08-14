from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.switch_soul_section import SwitchSoulSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.utils import add_left_row


class DemonEncounterSection(QGroupBox):
    name = "demon_encounter"

    def __init__(self, config):
        super().__init__("逢魔之时")
        self.config = config

        layout = QVBoxLayout(self)

        # 调度器配置
        self.scheduler_section = SchedulerSection(
            self.config, self.name)
        layout.addWidget(self.scheduler_section)

        # 御魂切换配置
        self.switch_soul_section = SwitchSoulSection(
            self.config, self.name)
        layout.addWidget(self.switch_soul_section)

        # 添加通用战斗配置
        self.general_battle_section = GeneralBattleSection(
            self.config, self.name)
        layout.addWidget(self.general_battle_section)

    def update_config(self):
        """更新配置"""

        # 添加调度设置
        self.scheduler_section.update_config()

        # 御魂切换设置
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
            logger.error(f"刷新结界突破设置UI时出错: {e}")
