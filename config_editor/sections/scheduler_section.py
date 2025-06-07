from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QLineEdit, QGroupBox)
from PyQt6.QtCore import Qt

class SchedulerSection(QGroupBox):
    def __init__(self, config, section_name):
        super().__init__("调度设置")
        self.config = config
        self.section_name = section_name
        self.scheduler_config = config[section_name]["scheduler"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 启用调度
        enable_layout = QHBoxLayout()
        self.enable_checkbox = QCheckBox("启用调度")
        self.enable_checkbox.setChecked(self.scheduler_config["enable"])
        enable_layout.addWidget(self.enable_checkbox)
        layout.addLayout(enable_layout)

        # 优先级
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("优先级:"))
        self.priority_spinbox = QSpinBox()
        self.priority_spinbox.setRange(0, 10)
        self.priority_spinbox.setValue(self.scheduler_config["priority"])
        priority_layout.addWidget(self.priority_spinbox)
        layout.addLayout(priority_layout)

        # 成功间隔
        success_layout = QHBoxLayout()
        success_layout.addWidget(QLabel("成功间隔:"))
        self.success_interval = QLineEdit()
        self.success_interval.setText(self.scheduler_config["success_interval"])
        success_layout.addWidget(self.success_interval)
        layout.addLayout(success_layout)

        # 失败间隔
        failure_layout = QHBoxLayout()
        failure_layout.addWidget(QLabel("失败间隔:"))
        self.failure_interval = QLineEdit()
        self.failure_interval.setText(self.scheduler_config["failure_interval"])
        failure_layout.addWidget(self.failure_interval)
        layout.addLayout(failure_layout)

    def update_config(self):
        self.scheduler_config["enable"] = self.enable_checkbox.isChecked()
        self.scheduler_config["priority"] = self.priority_spinbox.value()
        self.scheduler_config["success_interval"] = self.success_interval.text()
        self.scheduler_config["failure_interval"] = self.failure_interval.text() 