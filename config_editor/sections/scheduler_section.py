from PyQt6.QtWidgets import (QCheckBox, QComboBox, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit)
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton

def add_labeled_widget(layout, label_text, widget):
    row = QHBoxLayout()
    row.addWidget(QLabel(label_text))
    row.addWidget(widget)
    layout.addLayout(row)

class SchedulerSection(QGroupBox):
    def __init__(self, config, section_name):
        super().__init__("调度设置")
        self.config = config
        self.section_name = section_name
        layout = QVBoxLayout(self)
        scheduler = config[section_name].get("scheduler", {})

        # 启用调度
        self.enable_check = QCheckBox("启用调度")
        self.enable_check.setChecked(scheduler.get("enable", False))
        layout.addWidget(self.enable_check)

        # 优先级
        self.priority_spin = ValueButton()
        self.priority_spin.setRange(0, 9999)
        self.priority_spin.setValue(scheduler.get("priority", 0))
        add_labeled_widget(layout, "优先级", self.priority_spin)

        # 成功间隔
        success_interval_layout = QHBoxLayout()
        success_interval_layout.addWidget(QLabel("成功间隔:"))
        self.success_interval = QLineEdit()
        self.success_interval.setText(
            scheduler.get("success_interval", "00:00:00:00"))
        success_interval_layout.addWidget(self.success_interval)
        layout.addLayout(success_interval_layout)

        # 失败间隔
        failure_interval_layout = QHBoxLayout()
        failure_interval_layout.addWidget(QLabel("失败间隔:"))
        self.failure_interval = QLineEdit()
        self.failure_interval.setText(
            scheduler.get("failure_interval", "00:00:00:00"))
        failure_interval_layout.addWidget(self.failure_interval)
        layout.addLayout(failure_interval_layout)

        # 下次运行时间
        next_run_layout = QHBoxLayout()
        next_run_layout.addWidget(QLabel("下次运行时间:"))
        self.next_run = QLineEdit()
        self.next_run.setText(scheduler.get("next_run", "2023-01-01 00:00:00"))
        next_run_layout.addWidget(self.next_run)
        layout.addLayout(next_run_layout)

    def update_config(self):
        if "scheduler" not in self.config[self.section_name]:
            self.config[self.section_name]["scheduler"] = {}
        scheduler = self.config[self.section_name]["scheduler"]
        scheduler["enable"] = self.enable_check.isChecked()
        scheduler["priority"] = self.priority_spin.value()
        scheduler["success_interval"] = self.success_interval.text()
        scheduler["failure_interval"] = self.failure_interval.text()
        scheduler["next_run"] = self.next_run.text()
