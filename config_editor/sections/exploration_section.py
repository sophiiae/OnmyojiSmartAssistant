from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_left_row

class ExplorationSection(QGroupBox):
    def __init__(self, config):
        super().__init__("探索设置")
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

        # 加成设置（CheckBox独占一行）
        self.buff_gold_50 = QCheckBox("金币50%")
        self.buff_gold_50.setChecked(self.exploration_config["buff_gold_50"])
        add_left_row(exploration_layout, [self.buff_gold_50])

        self.buff_gold_100 = QCheckBox("金币100%")
        self.buff_gold_100.setChecked(self.exploration_config["buff_gold_100"])
        add_left_row(exploration_layout, [self.buff_gold_100])

        self.buff_exp_50 = QCheckBox("经验50%")
        self.buff_exp_50.setChecked(self.exploration_config["buff_exp_50"])
        add_left_row(exploration_layout, [self.buff_exp_50])

        self.buff_exp_100 = QCheckBox("经验100%")
        self.buff_exp_100.setChecked(self.exploration_config["buff_exp_100"])
        add_left_row(exploration_layout, [self.buff_exp_100])

        # 最大次数（无CheckBox，左对齐）
        self.count_max = ValueButton()
        self.count_max.setRange(1, 999)
        self.count_max.setValue(self.exploration_config["count_max"])
        add_left_row(exploration_layout, [QLabel("最大次数:"), self.count_max])

        # 章节（无CheckBox，左对齐）
        self.chapter = SelectButton()
        self.chapter.addItems(
            ["第一章", "第二章", "第三章", "第四章", "第五章", "第六章", "第七章", "第八章", "第九章", "第十章", "第十一章", "第十二章", "第十三章", "第十四章", "第十五章", "第十六章", "第十七章", "第十八章", "第十九章", "第二十章", "第二十一章", "第二十二章", "第二十三章", "第二十四章", "第二十五章", "第二十六章", "第二十七章", "第二十八章"])
        self.chapter.setCurrentText(self.exploration_config["chapter"])
        add_left_row(exploration_layout, [QLabel("章节:"), self.chapter])

        # 自动补充狗粮（CheckBox独占一行）
        self.auto_backup = QCheckBox("自动补充狗粮")
        self.auto_backup.setChecked(self.exploration_config["auto_backup"])
        add_left_row(exploration_layout, [self.auto_backup])

        # 狗粮稀有度（无CheckBox，左对齐）
        self.backup_rarity = SelectButton()
        self.backup_rarity.addItems(["素材", "N", "R", "SR", "SSR", "SP"])
        self.backup_rarity.setCurrentText(
            self.exploration_config["backup_rarity"])
        add_left_row(exploration_layout, [
                     QLabel("狗粮稀有度:"), self.backup_rarity])

        # 锁定队伍（CheckBox独占一行）
        self.lock_team_enable = QCheckBox("锁定队伍(勾选则狗粮配置失效)")
        self.lock_team_enable.setChecked(
            self.exploration_config["lock_team_enable"])
        add_left_row(exploration_layout, [self.lock_team_enable])

        layout.addWidget(exploration_group)

        # 卷轴设置
        scrolls_group = QGroupBox("卷轴设置")
        scrolls_layout = QVBoxLayout(scrolls_group)
        self.scrolls_config = self.config["exploration"]["scroll_mode"]

        # 启用卷轴模式（CheckBox独占一行）
        self.scroll_mode_enable = QCheckBox("启用卷轴模式")
        self.scroll_mode_enable.setChecked(
            self.scrolls_config["scroll_mode_enable"])
        add_left_row(scrolls_layout, [self.scroll_mode_enable])

        # 卷轴CD（无CheckBox，左对齐）
        self.scrolls_cd = QLineEdit()
        self.scrolls_cd.setText(self.scrolls_config["scrolls_cd"])
        add_left_row(scrolls_layout, [QLabel("卷轴CD:"), self.scrolls_cd])

        # 票数阈值（无CheckBox，左对齐）
        self.ticket_threshold = ValueButton()
        self.ticket_threshold.setRange(0, 999)
        self.ticket_threshold.setValue(self.scrolls_config["ticket_threshold"])
        add_left_row(scrolls_layout, [QLabel("票数阈值:"), self.ticket_threshold])

        layout.addWidget(scrolls_group)

        # 添加通用战斗配置
        self.general_battle_section = GeneralBattleSection(
            self.config, "exploration")
        layout.addWidget(self.general_battle_section)

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

        # 更新通用战斗配置
        self.general_battle_section.update_config()
