from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QSpinBox, QComboBox, QLabel, QLineEdit, QHBoxLayout

class RealmRaidSection(QGroupBox):
    def __init__(self, config):
        super().__init__("结界突破设置")
        self.config = config
        layout = QVBoxLayout(self)
        raid = config["realm_raid"]["raid_config"]
        row = QHBoxLayout()
        row.addWidget(QLabel("所需门票:"))
        self.tickets_spin = QSpinBox()
        self.tickets_spin.setRange(1, 100)
        self.tickets_spin.setValue(raid.get("tickets_required", 20))
        row.addWidget(self.tickets_spin)
        layout.addLayout(row)
        self.exit_two = QCheckBox("退出两次")
        self.exit_two.setChecked(raid.get("exit_two", False))
        layout.addWidget(self.exit_two)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("攻击顺序:"))
        self.order_edit = QLineEdit(str(raid.get("order_attack", "")))
        row2.addWidget(self.order_edit)
        layout.addLayout(row2)
        self.three_refresh = QCheckBox("三次刷新")
        self.three_refresh.setChecked(raid.get("three_refresh", False))
        layout.addWidget(self.three_refresh)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("攻击失败时:"))
        self.fail_combo = QComboBox()
        self.fail_combo.addItems(["Continue", "Stop", "Retry"])
        self.fail_combo.setCurrentText(
            raid.get("when_attack_fail", "Continue"))
        row3.addWidget(self.fail_combo)
        layout.addLayout(row3)

    def update_config(self):
        self.config["realm_raid"]["raid_config"]["tickets_required"] = self.tickets_spin.value()
        self.config["realm_raid"]["raid_config"]["exit_two"] = self.exit_two.isChecked()
        self.config["realm_raid"]["raid_config"]["order_attack"] = self.order_edit.text()
        self.config["realm_raid"]["raid_config"]["three_refresh"] = self.three_refresh.isChecked()
        self.config["realm_raid"]["raid_config"]["when_attack_fail"] = self.fail_combo.currentText()
