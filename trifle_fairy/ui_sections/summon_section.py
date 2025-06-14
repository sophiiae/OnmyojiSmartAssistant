from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QComboBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton

def add_left_row(layout, widgets):
    row = QHBoxLayout()
    for w in widgets:
        row.addWidget(w)
    layout.addLayout(row)

class SummonSection(QGroupBox):
    def __init__(self, config):
        super().__init__("召唤清票设置")
        self.config = config["summon"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加启用复选框
        self.enable_checkbox = QCheckBox("启用召唤清票")
        self.enable_checkbox.setChecked(self.config.get("enable", False))
        layout.addWidget(self.enable_checkbox)

        # 优先级（无CheckBox，左对齐）
        self.priority = ValueButton()
        self.priority.setRange(1, 5)
        self.priority.setValue(self.config["priority"])
        add_left_row(layout, [QLabel("优先级:"), self.priority])

        # 票数阈值（无CheckBox，左对齐）
        self.ticket_threshold = ValueButton()
        self.ticket_threshold.setRange(0, 999)
        self.ticket_threshold.setValue(self.config["ticket_threshold"])
        add_left_row(layout, [QLabel("票数阈值:"), self.ticket_threshold])

        # 最大次数（无CheckBox，左对齐）
        self.count_max = ValueButton()
        self.count_max.setRange(1, 5000)
        self.count_max.setValue(self.config["count_max"])
        add_left_row(layout, [QLabel("最大次数:"), self.count_max])

    def update_config(self):
        self.config["enable"] = self.enable_checkbox.isChecked()
        self.config["priority"] = self.priority.value()
        # 更新探索配置
        self.config["ticket_threshold"] = self.ticket_threshold.value()
        self.config["count_max"] = self.count_max.value()
