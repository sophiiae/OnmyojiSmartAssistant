from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.switch_soul_section import SwitchSoulSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_left_row

class AreaBossSection(QGroupBox):
    name = "area_boss"

    def __init__(self, config):
        super().__init__("地域鬼王设置")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, self.name)
        layout.addWidget(self.scheduler_section)

        # 鬼王配置
        boss_group = QGroupBox("地域鬼王")
        boss_layout = QVBoxLayout(boss_group)
        self.boss_config = self.config[self.name]["boss_config"]

        # 鬼王数量（无CheckBox，左对齐）
        self.boss_number_spin = ValueButton()
        self.boss_number_spin.setRange(0, 9999)
        self.boss_number_spin.setValue(self.boss_config.get("boss_number", 0))
        add_left_row(boss_layout, [QLabel("鬼王数量"), self.boss_number_spin])

        layout.addWidget(boss_group)

        # 御魂切换设置
        self.switch_soul_section = SwitchSoulSection(self.config, self.name)
        layout.addWidget(self.switch_soul_section)

        # 添加通用战斗配置
        self.general_battle_section = GeneralBattleSection(
            self.config, self.name)
        layout.addWidget(self.general_battle_section)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新鬼王配置
        self.boss_config["boss_number"] = self.boss_number_spin.value()

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
            logger.error(f"刷新地域鬼王设置UI时出错: {e}")
