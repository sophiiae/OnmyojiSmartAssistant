from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QCheckBox, QGroupBox, QLineEdit, QGridLayout)
from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.sections.switch_soul_section import SwitchSoulSection
from config_editor.sections.general_battle_section import GeneralBattleSection
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_checkbox_right_row, add_left_row

class ExplorationSection(QGroupBox):
    name = "exploration"

    def __init__(self, config):
        super().__init__("探索")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, self.name)
        layout.addWidget(self.scheduler_section)

        # 探索配置
        exploration_group = QGroupBox("探索配置")
        exploration_layout = QVBoxLayout(exploration_group)
        self.exploration_config = self.config[self.name]["exploration_config"]

        buff_grid = QGridLayout()

        self.buff_gold_50 = QCheckBox("金币50%")
        self.buff_gold_50.setChecked(self.exploration_config["buff_gold_50"])
        buff_grid.addWidget(self.buff_gold_50, 0, 0)

        self.buff_gold_100 = QCheckBox("金币100%")
        self.buff_gold_100.setChecked(self.exploration_config["buff_gold_100"])
        buff_grid.addWidget(self.buff_gold_100, 0, 1)

        self.buff_exp_50 = QCheckBox("经验50%")
        self.buff_exp_50.setChecked(self.exploration_config["buff_exp_50"])
        buff_grid.addWidget(self.buff_exp_50, 0, 2)

        self.buff_exp_100 = QCheckBox("经验100%")
        self.buff_exp_100.setChecked(self.exploration_config["buff_exp_100"])
        buff_grid.addWidget(self.buff_exp_100, 0, 3)

        group = QGroupBox("战斗加成配置")
        group.setLayout(buff_grid)
        layout.addWidget(group)

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

        # 难度（无CheckBox，左对齐）
        self.chapter_hardness = SelectButton()
        self.chapter_hardness.addItems(["随机", "普通", "困难"])
        self.chapter_hardness.setCurrentText(
            self.exploration_config["chapter_hardness"])
        add_left_row(exploration_layout, [
                     QLabel("章节难度:"), self.chapter_hardness])

        # 自动补充狗粮（CheckBox独占一行）
        self.auto_backup = QCheckBox("自动补充狗粮")
        self.auto_backup.setChecked(self.exploration_config["auto_backup"])
        add_left_row(exploration_layout, [self.auto_backup])

        # 自动清御魂（CheckBox独占一行）
        self.auto_soul_clear = QCheckBox("自动清御魂")
        self.auto_soul_clear.setChecked(
            self.exploration_config["auto_soul_clear"])
        add_left_row(exploration_layout, [self.auto_soul_clear])

        # 狗粮稀有度（无CheckBox，左对齐）
        self.backup_rarity = SelectButton()
        self.backup_rarity.addItems(["素材", "N", "R", "SR", "SSR", "SP"])
        self.backup_rarity.setCurrentText(
            self.exploration_config["backup_rarity"])
        add_left_row(exploration_layout, [
                     QLabel("狗粮稀有度:"), self.backup_rarity])

        layout.addWidget(exploration_group)

        # 绘卷设置
        scrolls_group = QGroupBox("绘卷设置")
        scrolls_layout = QVBoxLayout(scrolls_group)
        self.scrolls_config = self.config[self.name]["scroll_mode"]

        # 启用绘卷模式（CheckBox独占一行）
        self.scroll_mode_enable = QCheckBox("启用绘卷模式")
        self.scroll_mode_enable.setChecked(
            self.scrolls_config["scroll_mode_enable"])

        # 绘卷CD（无CheckBox，左对齐）
        self.scrolls_cd = QLineEdit()
        self.scrolls_cd.setText(self.scrolls_config["scrolls_cd"])

        add_checkbox_right_row(scrolls_layout, self.scroll_mode_enable, [
            QLabel("绘卷CD:"), self.scrolls_cd])

        # 票数阈值（无CheckBox，左对齐）
        self.ticket_threshold = ValueButton()
        self.ticket_threshold.setRange(0, 999)
        self.ticket_threshold.setValue(self.scrolls_config["ticket_threshold"])
        add_left_row(scrolls_layout, [QLabel("票数阈值:"), self.ticket_threshold])

        layout.addWidget(scrolls_group)

        # 御魂切换设置
        self.switch_soul_section = SwitchSoulSection(
            self.config, self.name)
        layout.addWidget(self.switch_soul_section)

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
        self.exploration_config["chapter_hardness"] = self.chapter_hardness.currentText(
        )
        self.exploration_config["auto_backup"] = self.auto_backup.isChecked()
        self.exploration_config["backup_rarity"] = self.backup_rarity.currentText(
        )

        # 更新绘卷设置
        self.scrolls_config["scroll_mode_enable"] = self.scroll_mode_enable.isChecked(
        )
        self.scrolls_config["scrolls_cd"] = self.scrolls_cd.text()
        self.scrolls_config["ticket_threshold"] = self.ticket_threshold.value()

        # 更新御魂切换配置
        self.switch_soul_section.update_config()

    def refresh_from_config(self, config):
        """根据配置刷新UI控件"""
        try:
            # 更新内部配置引用
            self.config = config

            # 刷新调度器设置
            if hasattr(self.scheduler_section, 'refresh_from_config'):
                self.scheduler_section.refresh_from_config(config)

        except Exception as e:
            from module.base.logger import logger
            logger.error(f"刷新探索设置UI时出错: {e}")
