from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QSpinBox, QLabel, QLineEdit, QHBoxLayout

class AreaBossSection(QGroupBox):
    def __init__(self, config):
        super().__init__("地域BOSS设置")
        self.config = config
        layout = QVBoxLayout(self)
        boss = config["area_boss"]["boss"]
        row = QHBoxLayout()
        row.addWidget(QLabel("BOSS数量:"))
        self.boss_number_spin = QSpinBox()
        self.boss_number_spin.setRange(1, 10)
        self.boss_number_spin.setValue(boss.get("boss_number", 3))
        row.addWidget(self.boss_number_spin)
        layout.addLayout(row)
        self.boss_reward = QCheckBox("BOSS奖励")
        self.boss_reward.setChecked(boss.get("boss_reward", False))
        layout.addWidget(self.boss_reward)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("奖励层数:"))
        self.reward_floor_edit = QLineEdit(str(boss.get("reward_floor", "一星")))
        row2.addWidget(self.reward_floor_edit)
        layout.addLayout(row2)
        self.use_collect = QCheckBox("使用收集")
        self.use_collect.setChecked(boss.get("use_collect", False))
        layout.addWidget(self.use_collect)
        self.Attack_60 = QCheckBox("攻击60")
        self.Attack_60.setChecked(boss.get("Attack_60", False))
        layout.addWidget(self.Attack_60)

    def update_config(self):
        self.config["area_boss"]["boss"]["boss_number"] = self.boss_number_spin.value()
        self.config["area_boss"]["boss"]["boss_reward"] = self.boss_reward.isChecked()
        self.config["area_boss"]["boss"]["reward_floor"] = self.reward_floor_edit.text()
        self.config["area_boss"]["boss"]["use_collect"] = self.use_collect.isChecked()
        self.config["area_boss"]["boss"]["Attack_60"] = self.Attack_60.isChecked()
