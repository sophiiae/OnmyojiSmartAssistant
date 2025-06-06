from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QSpinBox, QComboBox, QLabel, QHBoxLayout

class ExplorationSection(QGroupBox):
    def __init__(self, config):
        super().__init__("探索设置")
        self.config = config
        layout = QVBoxLayout(self)
        exp_cfg = config["exploration"]["exploration_config"]
        self.buff_gold_50 = QCheckBox("50%金币加成")
        self.buff_gold_50.setChecked(exp_cfg.get("buff_gold_50", False))
        layout.addWidget(self.buff_gold_50)
        self.buff_gold_100 = QCheckBox("100%金币加成")
        self.buff_gold_100.setChecked(exp_cfg.get("buff_gold_100", False))
        layout.addWidget(self.buff_gold_100)
        self.buff_exp_50 = QCheckBox("50%经验加成")
        self.buff_exp_50.setChecked(exp_cfg.get("buff_exp_50", False))
        layout.addWidget(self.buff_exp_50)
        self.buff_exp_100 = QCheckBox("100%经验加成")
        self.buff_exp_100.setChecked(exp_cfg.get("buff_exp_100", False))
        layout.addWidget(self.buff_exp_100)
        row = QHBoxLayout()
        row.addWidget(QLabel("最大次数:"))
        self.count_max_spin = QSpinBox()
        self.count_max_spin.setRange(1, 100)
        self.count_max_spin.setValue(exp_cfg.get("count_max", 10))
        row.addWidget(self.count_max_spin)
        layout.addLayout(row)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("章节:"))
        self.chapter_combo = QComboBox()
        self.chapter_combo.addItems([f"第{i}章" for i in range(1, 29)])
        self.chapter_combo.setCurrentText(exp_cfg.get("chapter", "第二十八章"))
        row2.addWidget(self.chapter_combo)
        layout.addLayout(row2)

    def update_config(self):
        self.config["exploration"]["exploration_config"]["buff_gold_50"] = self.buff_gold_50.isChecked()
        self.config["exploration"]["exploration_config"]["buff_gold_100"] = self.buff_gold_100.isChecked()
        self.config["exploration"]["exploration_config"]["buff_exp_50"] = self.buff_exp_50.isChecked()
        self.config["exploration"]["exploration_config"]["buff_exp_100"] = self.buff_exp_100.isChecked()
        self.config["exploration"]["exploration_config"]["count_max"] = self.count_max_spin.value()
        self.config["exploration"]["exploration_config"]["chapter"] = self.chapter_combo.currentText()
