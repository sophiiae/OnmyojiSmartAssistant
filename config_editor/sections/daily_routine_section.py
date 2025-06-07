from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QGroupBox, QGridLayout, QSpinBox, QComboBox)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.widgets.select_button import SelectButton
from config_editor.widgets.value_button import ValueButton

class DailyRoutineSection(QGroupBox):
    def __init__(self, config):
        super().__init__("日常任务设置")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        daily_config = self.config["daily_routine"]

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "daily_routine")
        layout.addWidget(self.scheduler_section)

        # 日常登录奖励配置
        rewards = daily_config.get("login_rewards", {})
        reward_names = [
            "领取勾玉", "签到", "签到999", "领取邮件", "领取御魂", "领取体力",
        ]
        self.reward_checkboxes = []
        grid = QGridLayout()
        for i, name in enumerate(reward_names):
            cb = QCheckBox(name)
            cb.setChecked(rewards.get(name, False))
            self.reward_checkboxes.append(cb)
            row, col = divmod(i, 3)
            grid.addWidget(cb, row, col)
        group = QGroupBox("日常登录奖励配置")
        group.setLayout(grid)
        layout.addWidget(group)

        # 杂项配置
        trifles_group = QGroupBox("杂项配置")
        trifles_layout = QVBoxLayout(trifles_group)
        self.trifles_config = daily_config["trifles_config"]

        self.one_summon = QCheckBox("单抽")
        self.one_summon.setChecked(self.trifles_config["one_summon"])
        trifles_layout.addWidget(self.one_summon)

        self.guild_wish = QCheckBox("寮祈愿")
        self.guild_wish.setChecked(self.trifles_config["guild_wish"])
        trifles_layout.addWidget(self.guild_wish)

        self.friend_love = QCheckBox("好友爱心")
        self.friend_love.setChecked(self.trifles_config["friend_love"])
        trifles_layout.addWidget(self.friend_love)

        self.store_sign = QCheckBox("商店签到")
        self.store_sign.setChecked(self.trifles_config["store_sign"])
        trifles_layout.addWidget(self.store_sign)

        layout.addWidget(trifles_group)

        # 优先级设置
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("优先级:"))
        self.priority = SelectButton()
        self.priority.addItems(["1", "2", "3", "4", "5"])
        self.priority.setCurrentText(str(daily_config.get("priority", 1)))
        priority_layout.addWidget(self.priority)
        priority_layout.addStretch()
        layout.addLayout(priority_layout)

    def update_config(self):
        self.scheduler_section.update_config()

        rewards = self.config["daily_routine"].setdefault("login_rewards", {})
        for cb in self.reward_checkboxes:
            rewards[cb.text()] = cb.isChecked()

        # 更新杂项配置
        self.trifles_config["one_summon"] = self.one_summon.isChecked()
        self.trifles_config["guild_wish"] = self.guild_wish.isChecked()
        self.trifles_config["friend_love"] = self.friend_love.isChecked()
        self.trifles_config["store_sign"] = self.store_sign.isChecked()

        self.config["daily_routine"]["priority"] = int(
            self.priority.currentText())
