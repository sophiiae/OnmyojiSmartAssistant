from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QComboBox, QGroupBox)
from config_editor.sections.scheduler_section import SchedulerSection

class AreaBossSection(QGroupBox):
    def __init__(self, config):
        super().__init__("地域鬼王")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "area_boss")
        layout.addWidget(self.scheduler_section)

        # 鬼王配置
        boss_group = QGroupBox("鬼王配置")
        boss_layout = QVBoxLayout(boss_group)
        self.boss_config = self.config["area_boss"]["boss"]

        boss_number_layout = QHBoxLayout()
        boss_number_layout.addWidget(QLabel("鬼王数量:"))
        self.boss_number = QSpinBox()
        self.boss_number.setRange(1, 5)
        self.boss_number.setValue(self.boss_config["boss_number"])
        boss_number_layout.addWidget(self.boss_number)
        boss_layout.addLayout(boss_number_layout)

        self.boss_reward = QCheckBox("领取奖励")
        self.boss_reward.setChecked(self.boss_config["boss_reward"])
        boss_layout.addWidget(self.boss_reward)

        reward_floor_layout = QHBoxLayout()
        reward_floor_layout.addWidget(QLabel("奖励星级:"))
        self.reward_floor = QComboBox()
        self.reward_floor.addItems(["一星", "二星", "三星"])
        self.reward_floor.setCurrentText(self.boss_config["reward_floor"])
        reward_floor_layout.addWidget(self.reward_floor)
        boss_layout.addLayout(reward_floor_layout)

        self.use_collect = QCheckBox("使用集结")
        self.use_collect.setChecked(self.boss_config["use_collect"])
        boss_layout.addWidget(self.use_collect)

        self.Attack_60 = QCheckBox("60秒攻击")
        self.Attack_60.setChecked(self.boss_config["Attack_60"])
        boss_layout.addWidget(self.Attack_60)

        layout.addWidget(boss_group)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新鬼王配置
        self.boss_config["boss_number"] = self.boss_number.value()
        self.boss_config["boss_reward"] = self.boss_reward.isChecked()
        self.boss_config["reward_floor"] = self.reward_floor.currentText()
        self.boss_config["use_collect"] = self.use_collect.isChecked()
        self.boss_config["Attack_60"] = self.Attack_60.isChecked()
