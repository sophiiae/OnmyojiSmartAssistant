from PyQt6.QtWidgets import (
    QCheckBox, QGroupBox, QVBoxLayout, QLabel, QLineEdit)
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.utils import add_left_row

class GoryouRealmSection(QGroupBox):
    def __init__(self, config):
        super().__init__("御灵设置")
        self.config = config

        # 确保所有必需的配置项存在
        if "goryou_realm" not in self.config:
            self.config["goryou_realm"] = {}
        goryou_realm = self.config["goryou_realm"]

        if "scheduler" not in goryou_realm:
            goryou_realm["scheduler"] = {
                "enable": False,
                "next_run": "2023-01-01 00:00:00",
                "priority": 5,
                "success_interval": "00:00:30:00",
                "failure_interval": "00:00:10:00"
            }

        if "goryou_config" not in goryou_realm:
            goryou_realm["goryou_config"] = {
                "goryou_class": "暗孔雀",
                "count_max": 50,
                "level": "三层",
                "lock_team_enable": True
            }

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
        switch_soul_group = QGroupBox("御魂切换设置")
        switch_soul_layout = QVBoxLayout(switch_soul_group)
        self.switch_soul_config = self.config["goryou_realm"]["switch_soul_config"]

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

    def update_config(self):
        self.scheduler_section.update_config()

        goryou_config = self.config["goryou_realm"]["goryou_config"]
        goryou_config["goryou_class"] = self.goryou_type_combo.currentText()
        goryou_config["count_max"] = self.max_count_spin.value()
        goryou_config["level"] = self.level_combo.currentText()
        goryou_config["lock_team_enable"] = self.lock_team_enable.isChecked()

        # 更新御魂切换配置
        self.switch_soul_config["enable"] = self.switch_soul_enable.isChecked()
        self.switch_soul_config["switch_group_team"] = self.switch_group_team.text(
        )
