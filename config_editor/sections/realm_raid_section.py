from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QComboBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection

class RealmRaidSection(QGroupBox):
    def __init__(self, config):
        super().__init__("结界突破")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "realm_raid")
        layout.addWidget(self.scheduler_section)

        # 突破配置
        raid_group = QGroupBox("突破配置")
        raid_layout = QVBoxLayout(raid_group)
        self.raid_config = self.config["realm_raid"]["raid_config"]

        tickets_layout = QHBoxLayout()
        tickets_layout.addWidget(QLabel("所需票数:"))
        self.tickets_required = QSpinBox()
        self.tickets_required.setRange(0, 999)
        self.tickets_required.setValue(self.raid_config["tickets_required"])
        tickets_layout.addWidget(self.tickets_required)
        raid_layout.addLayout(tickets_layout)

        self.exit_two = QCheckBox("退出二次")
        self.exit_two.setChecked(self.raid_config["exit_two"])
        raid_layout.addWidget(self.exit_two)

        order_layout = QHBoxLayout()
        order_layout.addWidget(QLabel("攻击顺序:"))
        self.order_attack = QLineEdit()
        self.order_attack.setText(self.raid_config["order_attack"])
        order_layout.addWidget(self.order_attack)
        raid_layout.addLayout(order_layout)

        self.three_refresh = QCheckBox("三次刷新")
        self.three_refresh.setChecked(self.raid_config["three_refresh"])
        raid_layout.addWidget(self.three_refresh)

        when_attack_fail_layout = QHBoxLayout()
        when_attack_fail_layout.addWidget(QLabel("攻击失败时:"))
        self.when_attack_fail = QComboBox()
        self.when_attack_fail.addItems(["Continue", "Exit"])
        self.when_attack_fail.setCurrentText(
            self.raid_config["when_attack_fail"])
        when_attack_fail_layout.addWidget(self.when_attack_fail)
        raid_layout.addLayout(when_attack_fail_layout)

        layout.addWidget(raid_group)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新突破配置
        self.raid_config["tickets_required"] = self.tickets_required.value()
        self.raid_config["exit_two"] = self.exit_two.isChecked()
        self.raid_config["order_attack"] = self.order_attack.text()
        self.raid_config["three_refresh"] = self.three_refresh.isChecked()
        self.raid_config["when_attack_fail"] = self.when_attack_fail.currentText()
