from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QSpinBox, QComboBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection

class ExplorationSection(QGroupBox):
    def __init__(self, config):
        super().__init__("探索")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "exploration")
        layout.addWidget(self.scheduler_section)

        # 探索配置
        exploration_group = QGroupBox("探索配置")
        exploration_layout = QVBoxLayout(exploration_group)
        self.exploration_config = self.config["exploration"]["exploration_config"]

        # 加成设置
        buff_layout = QHBoxLayout()
        self.buff_gold_50 = QCheckBox("金币50%")
        self.buff_gold_50.setChecked(self.exploration_config["buff_gold_50"])
        buff_layout.addWidget(self.buff_gold_50)

        self.buff_gold_100 = QCheckBox("金币100%")
        self.buff_gold_100.setChecked(self.exploration_config["buff_gold_100"])
        buff_layout.addWidget(self.buff_gold_100)

        self.buff_exp_50 = QCheckBox("经验50%")
        self.buff_exp_50.setChecked(self.exploration_config["buff_exp_50"])
        buff_layout.addWidget(self.buff_exp_50)

        self.buff_exp_100 = QCheckBox("经验100%")
        self.buff_exp_100.setChecked(self.exploration_config["buff_exp_100"])
        buff_layout.addWidget(self.buff_exp_100)
        exploration_layout.addLayout(buff_layout)

        # 其他设置
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("最大次数:"))
        self.count_max = QSpinBox()
        self.count_max.setRange(1, 999)
        self.count_max.setValue(self.exploration_config["count_max"])
        count_layout.addWidget(self.count_max)
        exploration_layout.addLayout(count_layout)

        chapter_layout = QHBoxLayout()
        chapter_layout.addWidget(QLabel("章节:"))
        self.chapter = QComboBox()
        self.chapter.addItems(
            ["第1章", "第2章", "第3章", "第4章", "第5章", "第6章", "第7章", "第8章", "第9章", "第10章"])
        self.chapter.setCurrentText(self.exploration_config["chapter"])
        chapter_layout.addWidget(self.chapter)
        exploration_layout.addLayout(chapter_layout)

        self.auto_backup = QCheckBox("自动备份")
        self.auto_backup.setChecked(self.exploration_config["auto_backup"])
        exploration_layout.addWidget(self.auto_backup)

        backup_rarity_layout = QHBoxLayout()
        backup_rarity_layout.addWidget(QLabel("备份稀有度:"))
        self.backup_rarity = QComboBox()
        self.backup_rarity.addItems(["素材", "N", "R", "SR", "SSR", "SP"])
        self.backup_rarity.setCurrentText(
            self.exploration_config["backup_rarity"])
        backup_rarity_layout.addWidget(self.backup_rarity)
        exploration_layout.addLayout(backup_rarity_layout)

        self.lock_team_enable = QCheckBox("锁定队伍")
        self.lock_team_enable.setChecked(
            self.exploration_config["lock_team_enable"])
        exploration_layout.addWidget(self.lock_team_enable)

        layout.addWidget(exploration_group)

        # 卷轴设置
        scrolls_group = QGroupBox("卷轴设置")
        scrolls_layout = QVBoxLayout(scrolls_group)
        self.scrolls_config = self.config["exploration"]["scrolls"]

        self.scroll_mode_enable = QCheckBox("启用卷轴模式")
        self.scroll_mode_enable.setChecked(
            self.scrolls_config["scroll_mode_enable"])
        scrolls_layout.addWidget(self.scroll_mode_enable)

        scrolls_cd_layout = QHBoxLayout()
        scrolls_cd_layout.addWidget(QLabel("卷轴CD:"))
        self.scrolls_cd = QLineEdit()
        self.scrolls_cd.setText(self.scrolls_config["scrolls_cd"])
        scrolls_cd_layout.addWidget(self.scrolls_cd)
        scrolls_layout.addLayout(scrolls_cd_layout)

        ticket_threshold_layout = QHBoxLayout()
        ticket_threshold_layout.addWidget(QLabel("票数阈值:"))
        self.ticket_threshold = QSpinBox()
        self.ticket_threshold.setRange(0, 999)
        self.ticket_threshold.setValue(self.scrolls_config["ticket_threshold"])
        ticket_threshold_layout.addWidget(self.ticket_threshold)
        scrolls_layout.addLayout(ticket_threshold_layout)

        layout.addWidget(scrolls_group)

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新探索配置
        self.exploration_config["buff_gold_50"] = self.buff_gold_50.isChecked()
        self.exploration_config["buff_gold_100"] = self.buff_gold_100.isChecked(
        )
        self.exploration_config["buff_exp_50"] = self.buff_exp_50.isChecked()
        self.exploration_config["buff_exp_100"] = self.buff_exp_100.isChecked()
        self.exploration_config["count_max"] = self.count_max.value()
        self.exploration_config["chapter"] = self.chapter.currentText()
        self.exploration_config["auto_backup"] = self.auto_backup.isChecked()
        self.exploration_config["backup_rarity"] = self.backup_rarity.currentText(
        )
        self.exploration_config["lock_team_enable"] = self.lock_team_enable.isChecked(
        )

        # 更新卷轴设置
        self.scrolls_config["scroll_mode_enable"] = self.scroll_mode_enable.isChecked(
        )
        self.scrolls_config["scrolls_cd"] = self.scrolls_cd.text()
        self.scrolls_config["ticket_threshold"] = self.ticket_threshold.value()
