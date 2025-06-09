from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QComboBox, QGroupBox, QLineEdit)
from PyQt6.QtCore import Qt
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

class RoyalBattleSection(QGroupBox):
    def __init__(self, config):
        super().__init__("斗技设置")
        self.config = config["royal_battle"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加启用复选框
        self.enable_checkbox = QCheckBox("启用斗技")
        self.enable_checkbox.setChecked(self.config.get("enable", False))
        layout.addWidget(self.enable_checkbox)

        self.grade_threshold = ValueButton()
        self.grade_threshold.setRange(0, 9999)
        self.grade_threshold.setValue(
            self.config.get("grade_threshold", 0))
        add_left_row(layout, [QLabel("斗技目标分数"), self.grade_threshold])

    def update_config(self):
        self.config["enable"] = self.enable_checkbox.isChecked()
        self.config["grade_threshold"] = self.grade_threshold.value()
