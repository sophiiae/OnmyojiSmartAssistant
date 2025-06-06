from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QSpinBox, QLabel, QHBoxLayout

class ShikigamiActivitySection(QGroupBox):
    def __init__(self, config):
        super().__init__("式神活动设置")
        self.config = config
        layout = QVBoxLayout(self)
        climb = config["shikigami_activity"]["climb_config"]
        self.enable_ap_mode = QCheckBox("启用体力模式")
        self.enable_ap_mode.setChecked(climb.get("enable_ap_mode", False))
        layout.addWidget(self.enable_ap_mode)
        self.auto_switch = QCheckBox("自动切换")
        self.auto_switch.setChecked(climb.get("auto_switch", False))
        layout.addWidget(self.auto_switch)
        row = QHBoxLayout()
        row.addWidget(QLabel("最大门票:"))
        self.ticket_max_spin = QSpinBox()
        self.ticket_max_spin.setRange(1, 100)
        self.ticket_max_spin.setValue(climb.get("ticket_max", 50))
        row.addWidget(self.ticket_max_spin)
        layout.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("最大体力:"))
        self.ap_max_spin = QSpinBox()
        self.ap_max_spin.setRange(1, 1000)
        self.ap_max_spin.setValue(climb.get("ap_max", 300))
        row2.addWidget(self.ap_max_spin)
        layout.addLayout(row2)
        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(climb.get("lock_team_enable", False))
        layout.addWidget(self.lock_team_enable)

    def update_config(self):
        self.config["shikigami_activity"]["climb_config"]["enable_ap_mode"] = self.enable_ap_mode.isChecked()
        self.config["shikigami_activity"]["climb_config"]["auto_switch"] = self.auto_switch.isChecked()
        self.config["shikigami_activity"]["climb_config"]["ticket_max"] = self.ticket_max_spin.value()
        self.config["shikigami_activity"]["climb_config"]["ap_max"] = self.ap_max_spin.value()
        self.config["shikigami_activity"]["climb_config"]["lock_team_enable"] = self.lock_team_enable.isChecked()
