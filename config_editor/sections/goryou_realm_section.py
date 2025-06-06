from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QComboBox, QSpinBox, QLabel, QCheckBox, QHBoxLayout

class GoryouRealmSection(QGroupBox):
    def __init__(self, config):
        super().__init__("御灵设置")
        self.config = config
        layout = QVBoxLayout(self)
        goryou = config["goryou_realm"]["goryou_config"]
        row = QHBoxLayout()
        row.addWidget(QLabel("御灵类型:"))
        self.goryou_class_combo = QComboBox()
        self.goryou_class_combo.addItems(["暗孔雀", "白藏主", "黑豹", "神龙"])
        self.goryou_class_combo.setCurrentText(
            goryou.get("goryou_class", "暗孔雀"))
        row.addWidget(self.goryou_class_combo)
        layout.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("最大次数:"))
        self.goryou_count_spin = QSpinBox()
        self.goryou_count_spin.setRange(1, 100)
        self.goryou_count_spin.setValue(goryou.get("count_max", 50))
        row2.addWidget(self.goryou_count_spin)
        layout.addLayout(row2)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("层数:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["一层", "二层", "三层"])
        self.level_combo.setCurrentText(goryou.get("level", "三层"))
        row3.addWidget(self.level_combo)
        layout.addLayout(row3)
        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(goryou.get("lock_team_enable", False))
        layout.addWidget(self.lock_team_enable)

    def update_config(self):
        self.config["goryou_realm"]["goryou_config"]["goryou_class"] = self.goryou_class_combo.currentText()
        self.config["goryou_realm"]["goryou_config"]["count_max"] = self.goryou_count_spin.value()
        self.config["goryou_realm"]["goryou_config"]["level"] = self.level_combo.currentText()
        self.config["goryou_realm"]["goryou_config"]["lock_team_enable"] = self.lock_team_enable.isChecked()
