from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_left_row

class RealmRaidSection(QGroupBox):
    def __init__(self, config):
        super().__init__("结界突破设置")
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

        # 所需票数（无CheckBox，左对齐）
        self.tickets_required = ValueButton()
        self.tickets_required.setRange(0, 999)
        self.tickets_required.setValue(self.raid_config["tickets_required"])
        add_left_row(raid_layout, [QLabel("所需票数:"), self.tickets_required])

        # 退出二次（CheckBox独占一行）
        self.exit_two = QCheckBox("退出二次")
        self.exit_two.setChecked(self.raid_config["exit_two"])
        add_left_row(raid_layout, [self.exit_two])

        # 攻击顺序（无CheckBox，左对齐）
        self.order_attack = QLineEdit()
        self.order_attack.setText(self.raid_config["order_attack"])
        add_left_row(raid_layout, [QLabel("攻击顺序:"), self.order_attack])

        # 三次刷新（CheckBox独占一行）
        self.three_refresh = QCheckBox("三次刷新")
        self.three_refresh.setChecked(self.raid_config["three_refresh"])
        add_left_row(raid_layout, [self.three_refresh])

        # 攻击失败时（无CheckBox，左对齐）
        self.when_attack_fail = SelectButton()
        self.when_attack_fail.addItems(["Continue", "Exit"])
        self.when_attack_fail.setCurrentText(
            self.raid_config["when_attack_fail"])
        add_left_row(raid_layout, [QLabel("攻击失败时:"), self.when_attack_fail])

        layout.addWidget(raid_group)

        # 添加通用战斗配置
        self.general_battle_section = GeneralBattleSection(
            self.config, "realm_raid")
        layout.addWidget(self.general_battle_section)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新突破配置
        self.raid_config["tickets_required"] = self.tickets_required.value()
        self.raid_config["exit_two"] = self.exit_two.isChecked()
        self.raid_config["order_attack"] = self.order_attack.text()
        self.raid_config["three_refresh"] = self.three_refresh.isChecked()
        self.raid_config["when_attack_fail"] = self.when_attack_fail.currentText()

        # 更新通用战斗配置
        self.general_battle_section.update_config()
