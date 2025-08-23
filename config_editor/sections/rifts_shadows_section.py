from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.switch_soul_section import SwitchSoulSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_left_row

class RiftsShadowsSection(QGroupBox):
    name = "rifts_shadows"

    def __init__(self, config):
        super().__init__("狭间暗域设置")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, self.name)
        layout.addWidget(self.scheduler_section)

        # 狭间配置
        rs_config_group = QGroupBox("狭间暗域")
        rs_config_layout = QVBoxLayout(rs_config_group)
        rifts_shadows_config = self.config[self.name]["rifts_shadows_config"]

        # 狭间首领分数（无CheckBox，左对齐）
        self.leader_battle_time = ValueButton()
        self.leader_battle_time.setRange(1, 180)
        self.leader_battle_time.setValue(
            rifts_shadows_config.get("leader_battle_time", 1))
        add_left_row(rs_config_layout, [QLabel(
            "首领战斗时长（秒）"), self.leader_battle_time])

        # 狭间副将分数（无CheckBox，左对齐）
        self.deputy_battle_time = ValueButton()
        self.deputy_battle_time.setRange(1, 180)
        self.deputy_battle_time.setValue(
            rifts_shadows_config.get("deputy_battle_time", 1))
        add_left_row(rs_config_layout, [QLabel(
            "副将战斗时长（秒）"), self.deputy_battle_time])

        # 狭间精英分数（无CheckBox，左对齐）
        self.elite_battle_time = ValueButton()
        self.elite_battle_time.setRange(1, 180)
        self.elite_battle_time.setValue(
            rifts_shadows_config.get("elite_battle_time", 1))
        add_left_row(rs_config_layout, [QLabel(
            "副将战斗时长（秒）"), self.elite_battle_time])

        layout.addWidget(rs_config_group)

        # 御魂切换设置
        self.switch_soul_section = SwitchSoulSection(self.config, self.name)
        layout.addWidget(self.switch_soul_section)

        # 添加通用战斗配置
        self.general_battle_section = GeneralBattleSection(
            self.config, self.name)
        layout.addWidget(self.general_battle_section)

    def update_config(self):
        self.scheduler_section.update_config()
        rs_config = self.config[self.name]["rifts_shadows_config"]

        # 更新狭间配置
        rs_config["leader_battle_time"] = self.leader_battle_time.value()
        rs_config["deputy_battle_time"] = self.deputy_battle_time.value()
        rs_config["elite_battle_time"] = self.elite_battle_time.value()

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
            logger.error(f"刷新狭间暗域设置UI时出错: {e}")
