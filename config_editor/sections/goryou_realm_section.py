from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QComboBox, QGroupBox)
from config_editor.sections.scheduler_section import SchedulerSection

class GoryouRealmSection(QGroupBox):
    def __init__(self, config):
        super().__init__("御灵")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "goryou_realm")
        layout.addWidget(self.scheduler_section)

        # 御灵配置
        goryou_group = QGroupBox("御灵配置")
        goryou_layout = QVBoxLayout(goryou_group)
        self.goryou_config = self.config["goryou_realm"]["goryou_config"]

        goryou_class_layout = QHBoxLayout()
        goryou_class_layout.addWidget(QLabel("御灵类型:"))
        self.goryou_class = QComboBox()
        self.goryou_class.addItems(["暗孔雀", "白藏主", "黑豹", "神龙"])
        self.goryou_class.setCurrentText(self.goryou_config["goryou_class"])
        goryou_class_layout.addWidget(self.goryou_class)
        goryou_layout.addLayout(goryou_class_layout)

        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("最大次数:"))
        self.count_max = QSpinBox()
        self.count_max.setRange(1, 999)
        self.count_max.setValue(self.goryou_config["count_max"])
        count_layout.addWidget(self.count_max)
        goryou_layout.addLayout(count_layout)

        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("层数:"))
        self.level = QComboBox()
        self.level.addItems(["一层", "二层", "三层"])
        self.level.setCurrentText(self.goryou_config["level"])
        level_layout.addWidget(self.level)
        goryou_layout.addLayout(level_layout)

        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(
            self.goryou_config["lock_team_enable"])
        goryou_layout.addWidget(self.lock_team_enable)

        layout.addWidget(goryou_group)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新御灵配置
        self.goryou_config["goryou_class"] = self.goryou_class.currentText()
        self.goryou_config["count_max"] = self.count_max.value()
        self.goryou_config["level"] = self.level.currentText()
        self.goryou_config["lock_team_enable"] = self.lock_team_enable.isChecked()
