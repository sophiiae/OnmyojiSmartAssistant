from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QGroupBox)
from config_editor.sections.scheduler_section import SchedulerSection

class ShikigamiActivitySection(QGroupBox):
    def __init__(self, config):
        super().__init__("式神活动")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "shikigami_activity")
        layout.addWidget(self.scheduler_section)

        # 爬塔配置
        climb_group = QGroupBox("爬塔配置")
        climb_layout = QVBoxLayout(climb_group)
        self.climb_config = self.config["shikigami_activity"]["climb_config"]

        self.enable_ap_mode = QCheckBox("启用体力模式")
        self.enable_ap_mode.setChecked(self.climb_config["enable_ap_mode"])
        climb_layout.addWidget(self.enable_ap_mode)

        self.auto_switch = QCheckBox("自动切换")
        self.auto_switch.setChecked(self.climb_config["auto_switch"])
        climb_layout.addWidget(self.auto_switch)

        ticket_max_layout = QHBoxLayout()
        ticket_max_layout.addWidget(QLabel("最大票数:"))
        self.ticket_max = QSpinBox()
        self.ticket_max.setRange(0, 999)
        self.ticket_max.setValue(self.climb_config["ticket_max"])
        ticket_max_layout.addWidget(self.ticket_max)
        climb_layout.addLayout(ticket_max_layout)

        ap_max_layout = QHBoxLayout()
        ap_max_layout.addWidget(QLabel("最大体力:"))
        self.ap_max = QSpinBox()
        self.ap_max.setRange(0, 999)
        self.ap_max.setValue(self.climb_config["ap_max"])
        ap_max_layout.addWidget(self.ap_max)
        climb_layout.addLayout(ap_max_layout)

        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(self.climb_config["lock_team_enable"])
        climb_layout.addWidget(self.lock_team_enable)

        layout.addWidget(climb_group)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新爬塔配置
        self.climb_config["enable_ap_mode"] = self.enable_ap_mode.isChecked()
        self.climb_config["auto_switch"] = self.auto_switch.isChecked()
        self.climb_config["ticket_max"] = self.ticket_max.value()
        self.climb_config["ap_max"] = self.ap_max.value()
        self.climb_config["lock_team_enable"] = self.lock_team_enable.isChecked()
