from PyQt6.QtWidgets import (
    QCheckBox, QGroupBox, QVBoxLayout, QLabel, QLineEdit)
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.switch_soul_section import SwitchSoulSection
from config_editor.utils import add_left_row

class GoryouRealmSection(QGroupBox):
    def __init__(self, config):
        super().__init__("御灵设置")
        self.config = config
        goryou_realm = self.config["goryou_realm"]

        layout = QVBoxLayout(self)
        goryou_config = goryou_realm["goryou_config"]

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "goryou_realm")
        layout.addWidget(self.scheduler_section)

        # 御灵类型（无CheckBox，左对齐）
        self.goryou_type_combo = SelectButton()
        self.goryou_type_combo.addItems(["随机", "白藏主", "黑豹", "孔雀", "九尾狐"])
        self.goryou_type_combo.setCurrentText(
            goryou_config.get("goryou_class", "暗孔雀"))
        add_left_row(layout, [QLabel("御灵类型"), self.goryou_type_combo])

        # 最大次数（无CheckBox，左对齐）
        self.max_count_spin = ValueButton()
        self.max_count_spin.setRange(0, 9999)
        self.max_count_spin.setValue(goryou_config.get("count_max", 50))
        add_left_row(layout, [QLabel("最大次数"), self.max_count_spin])

        # 层数（无CheckBox，左对齐）
        self.level_combo = SelectButton()
        self.level_combo.addItems(["一层", "二层", "三层"])
        self.level_combo.setCurrentText(goryou_config.get("level", "三层"))
        add_left_row(layout, [QLabel("层数"), self.level_combo])

        # 锁定队伍（CheckBox独占一行）
        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(
            goryou_config.get("lock_team_enable", True))
        add_left_row(layout, [self.lock_team_enable])

        # 御魂切换设置
        self.switch_soul_section = SwitchSoulSection(
            self.config, "goryou_realm")
        layout.addWidget(self.switch_soul_section)

    def update_config(self):
        self.scheduler_section.update_config()

        goryou_config = self.config["goryou_realm"]["goryou_config"]
        goryou_config["goryou_class"] = self.goryou_type_combo.currentText()
        goryou_config["count_max"] = self.max_count_spin.value()
        goryou_config["level"] = self.level_combo.currentText()
        goryou_config["lock_team_enable"] = self.lock_team_enable.isChecked()

        # 更新御魂切换配置
        self.switch_soul_section.update_config()

    def refresh_from_config(self, config):
        """根据配置刷新UI控件"""
        try:
            # 更新内部配置引用
            self.config = config

            # 刷新调度器设置
            if hasattr(self.scheduler_section, 'refresh_from_config'):
                self.scheduler_section.refresh_from_config(config)

            # 重新获取配置引用
            goryou_realm = config.get("goryou_realm", {})
            goryou_config = goryou_realm.get("goryou_config", {})

            # 刷新御灵配置UI控件
            self.goryou_type_combo.setCurrentText(
                goryou_config.get("goryou_class", "暗孔雀"))
            self.max_count_spin.setValue(
                goryou_config.get("count_max", 50))
            self.level_combo.setCurrentText(
                goryou_config.get("level", "三层"))
            self.lock_team_enable.setChecked(
                goryou_config.get("lock_team_enable", True))

        except Exception as e:
            from module.base.logger import logger
            logger.error(f"刷新御灵设置UI时出错: {e}")
