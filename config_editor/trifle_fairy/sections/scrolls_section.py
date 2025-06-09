from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QComboBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton

def add_checkbox_right_row(layout, checkbox, right_widgets):
    row = QHBoxLayout()
    row.addWidget(checkbox)
    row.addStretch()
    for w in right_widgets:
        row.addWidget(w)
    layout.addLayout(row)

def add_left_row(layout, widgets):
    row = QHBoxLayout()
    for w in widgets:
        row.addWidget(w)
    layout.addLayout(row)

class ScrollsSection(QGroupBox):
    def __init__(self, config):
        super().__init__("绘卷[肝帝]设置")
        self.config = config["scrolls"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加启用复选框
        self.enable_checkbox = QCheckBox("启用绘卷")
        self.enable_checkbox.setChecked(self.config.get("enable", False))
        layout.addWidget(self.enable_checkbox)

        # 卷轴CD（无CheckBox，左对齐）
        self.scrolls_cd = QLineEdit()
        self.scrolls_cd.setText(self.config["scrolls_cd"])
        add_left_row(layout, [QLabel("卷轴CD:"), self.scrolls_cd])

        # 加成设置（CheckBox独占一行）
        self.buff_gold_50 = QCheckBox("金币50%")
        self.buff_gold_50.setChecked(self.config["buff_gold_50"])
        add_left_row(layout, [self.buff_gold_50])

        self.buff_gold_100 = QCheckBox("金币100%")
        self.buff_gold_100.setChecked(self.config["buff_gold_100"])
        add_left_row(layout, [self.buff_gold_100])

        self.buff_exp_50 = QCheckBox("经验50%")
        self.buff_exp_50.setChecked(self.config["buff_exp_50"])
        add_left_row(layout, [self.buff_exp_50])

        self.buff_exp_100 = QCheckBox("经验100%")
        self.buff_exp_100.setChecked(self.config["buff_exp_100"])
        add_left_row(layout, [self.buff_exp_100])

        # 最大次数（无CheckBox，左对齐）
        self.count_max = ValueButton()
        self.count_max.setRange(1, 999)
        self.count_max.setValue(self.config["count_max"])
        add_left_row(layout, [QLabel("最大次数:"), self.count_max])

        # 自动狗粮（CheckBox独占一行）
        self.auto_backup = QCheckBox("自动狗粮")
        self.auto_backup.setChecked(self.config["auto_backup"])
        add_left_row(layout, [self.auto_backup])

        # 狗粮稀有度（无CheckBox，左对齐）
        self.backup_rarity = SelectButton()
        self.backup_rarity.addItems(["素材", "N", "R", "SR", "SSR", "SP"])
        self.backup_rarity.setCurrentText(
            self.config["backup_rarity"])
        add_left_row(layout, [
                     QLabel("狗粮稀有度:"), self.backup_rarity])

        # 锁定队伍（CheckBox独占一行）
        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(
            self.config["lock_team_enable"])
        add_left_row(layout, [self.lock_team_enable])

        # 票数阈值（无CheckBox，左对齐）
        self.ticket_threshold = ValueButton()
        self.ticket_threshold.setRange(0, 999)
        self.ticket_threshold.setValue(self.config["ticket_threshold"])
        add_left_row(layout, [QLabel("票数阈值:"), self.ticket_threshold])

    def update_config(self):
        self.config["enable"] = self.enable_checkbox.isChecked()
        # 更新探索配置
        self.config["buff_gold_50"] = self.buff_gold_50.isChecked()
        self.config["buff_gold_100"] = self.buff_gold_100.isChecked(
        )
        self.config["buff_exp_50"] = self.buff_exp_50.isChecked()
        self.config["buff_exp_100"] = self.buff_exp_100.isChecked()
        self.config["count_max"] = self.count_max.value()
        self.config["auto_backup"] = self.auto_backup.isChecked()
        self.config["backup_rarity"] = self.backup_rarity.currentText(
        )
        self.config["lock_team_enable"] = self.lock_team_enable.isChecked(
        )

        # 更新卷轴设置
        self.config["scrolls_cd"] = self.scrolls_cd.text()
        self.config["ticket_threshold"] = self.ticket_threshold.value()
