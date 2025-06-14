from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QGroupBox)
from config_editor.widgets.value_button import ValueButton

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

class AreaBossSection(QGroupBox):
    def __init__(self, config):
        super().__init__("地域鬼王设置")
        self.config = config["area_boss"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加启用复选框
        self.enable_checkbox = QCheckBox("启用地域鬼王")
        self.enable_checkbox.setChecked(self.config.get("enable", False))
        layout.addWidget(self.enable_checkbox)

        # 优先级（无CheckBox，左对齐）
        self.priority = ValueButton()
        self.priority.setRange(1, 5)
        self.priority.setValue(self.config["priority"])
        add_left_row(layout, [QLabel("优先级:"), self.priority])

        # 鬼王数量（无CheckBox，左对齐）
        self.boss_number_spin = ValueButton()
        self.boss_number_spin.setRange(0, 9999)
        self.boss_number_spin.setValue(self.config.get("boss_number", 0))
        add_left_row(layout, [QLabel("鬼王数量"), self.boss_number_spin])

    def update_config(self):
        self.config["enable"] = self.enable_checkbox.isChecked()
        self.config["priority"] = self.priority.value()
        # 更新鬼王配置
        self.config["boss_number"] = self.boss_number_spin.value()
