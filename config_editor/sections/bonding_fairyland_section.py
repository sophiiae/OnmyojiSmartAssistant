from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.switch_soul_section import SwitchSoulSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_left_row

class BondingFairylandSection(QGroupBox):
    name = "bonding_fairyland"

    def __init__(self, config):
        super().__init__("契灵之境")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(
            self.config, self.name)
        layout.addWidget(self.scheduler_section)

        # 契灵配置
        bonding_group = QGroupBox("契灵配置")
        bonding_layout = QVBoxLayout(bonding_group)
        self.bonding_config = self.config[self.name]["bonding_config"]

        # 探查次数（无CheckBox，左对齐）
        self.explore_count_spin = ValueButton()
        self.explore_count_spin.setRange(0, 9999)
        self.explore_count_spin.setValue(
            self.bonding_config.get("explore_count", 30))
        add_left_row(bonding_layout, [QLabel("探查次数"), self.explore_count_spin])

        layout.addWidget(bonding_group)

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

        # 更新契灵配置
        self.bonding_config["explore_count"] = self.explore_count_spin.value()

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
            logger.error(f"刷新契灵之境设置UI时出错: {e}")
