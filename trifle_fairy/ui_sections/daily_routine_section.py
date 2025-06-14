from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QGroupBox, QGridLayout, QSpinBox, QComboBox)
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from trifle_fairy.ui_sections.utils import add_left_row

class DailyRoutineSection(QGroupBox):
    def __init__(self, config):
        super().__init__("日常任务设置")
        self.config = config["daily_routine"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加启用复选框
        self.enable_checkbox = QCheckBox("启用日常任务")
        self.enable_checkbox.setChecked(self.config.get("enable", False))
        layout.addWidget(self.enable_checkbox)

        # 优先级（无CheckBox，左对齐）
        self.priority = ValueButton()
        self.priority.setRange(1, 5)
        self.priority.setValue(self.config["priority"])
        add_left_row(layout, [QLabel("优先级:"), self.priority])

        # 日常登录奖励配置
        self.reward_names = [
            "领取勾玉", "签到", "签到999", "领取邮件", "领取御魂",
            "领取体力", "单抽", "好友爱心", "商店签到"
        ]
        self.reward_config_names = [
            "enable_jade", "enable_sign", "enable_sign_999", "enable_mail", "enable_soul",
            "enable_ap", "one_summon", "friend_love", "store_sign"
        ]

        self.reward_checkboxes = []
        grid = QGridLayout()
        for i, name in enumerate(self.reward_names):
            cb = QCheckBox(name)
            cb.setChecked(self.config.get(self.reward_config_names[i], False))
            self.reward_checkboxes.append(cb)
            row, col = divmod(i, 3)
            grid.addWidget(cb, row, col)
        group = QGroupBox("日常登录奖励配置")
        group.setLayout(grid)
        layout.addWidget(group)

    def update_config(self):
        self.config["enable"] = self.enable_checkbox.isChecked()
        self.config["priority"] = self.priority.value()
        for i, cb in enumerate(self.reward_checkboxes):
            self.config[self.reward_config_names[i]] = cb.isChecked()
