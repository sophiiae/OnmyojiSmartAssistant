from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.switch_soul_section import SwitchSoulSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_checkbox_right_row, add_left_row

class DuelSection(QGroupBox):
    name = "duel"

    def __init__(self, config):
        super().__init__("斗技配置")
        self.config = config
        dule_config = self.config[self.name]
        self.duel_config = dule_config["duel_config"]
        self.switch_soul_config = dule_config["switch_soul_config"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(
            self.config, self.name)
        layout.addWidget(self.scheduler_section)

        # 斗技配置
        duel_group = QGroupBox("斗技配置")
        duel_layout = QVBoxLayout(duel_group)

        # 上名士（只有CheckBox）
        self.elite_enable = QCheckBox("上名士")
        self.elite_enable.setChecked(self.duel_config["elite"])
        add_left_row(duel_layout, [self.elite_enable])

        # 打满荣誉积分（只有CheckBox）
        self.full_honor_points_enable = QCheckBox("打满荣誉积分")
        self.full_honor_points_enable.setChecked(
            self.duel_config["full_honor_points"])
        add_left_row(duel_layout, [self.full_honor_points_enable])

        # 段位（无CheckBox，左对齐）
        self.tier = SelectButton()
        self.tier.addItems(
            ["一段", "二段", "三段", "四段", "五段", "六段", "七段", "八段", "九段"])
        self.tier.setCurrentText(self.duel_config["tier"])
        add_left_row(duel_layout, [QLabel("段位:"), self.tier])

        # 阴阳师选择（无CheckBox，左对齐）
        self.onmyoji = SelectButton()
        self.onmyoji.addItems(["自动", "晴明", "源博雅", "神乐", "八百比丘尼", "源赖光"])
        self.onmyoji.setCurrentText(self.duel_config["onmyoji"])
        add_left_row(duel_layout, [QLabel("阴阳师:"), self.onmyoji])

        layout.addWidget(duel_group)

        # 御魂切换设置
        self.switch_soul_section = SwitchSoulSection(
            self.config, self.name)
        layout.addWidget(self.switch_soul_section)

        # 添加通用战斗配置
        self.general_battle_section = GeneralBattleSection(
            self.config, self.name)
        layout.addWidget(self.general_battle_section)

    def update_config(self):
        # 更新调度配置
        self.scheduler_section.update_config()

        self.duel_config["elite"] = self.elite_enable.isChecked()
        self.duel_config["tier"] = self.tier.currentText()
        self.duel_config["onmyoji"] = self.onmyoji.currentText()
        self.duel_config["full_honor_points"] = self.full_honor_points_enable.isChecked(
        )

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

            # 重新获取配置引用
            duel_section = config.get("duel", {})
            self.duel_config = duel_section.get("duel_config", {})
            self.switch_soul_config = duel_section.get(
                "switch_soul_config", {})

            # 刷新斗技配置UI控件
            self.elite_enable.setChecked(
                self.duel_config.get("elite", False))
            self.tier.setCurrentText(
                self.duel_config.get("tier", "一段"))
            self.full_honor_points_enable.setChecked(
                self.duel_config.get("full_honor_points", False))
            self.onmyoji.setCurrentText(
                self.duel_config.get("onmyoji", "自动"))

        except Exception as e:
            from module.base.logger import logger
            logger.error(f"刷新斗技设置UI时出错: {e}")
