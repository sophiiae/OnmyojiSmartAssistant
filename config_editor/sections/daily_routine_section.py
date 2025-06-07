from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QCheckBox, QGroupBox)
from config_editor.sections.scheduler_section import SchedulerSection

class DailyRoutineSection(QGroupBox):
    def __init__(self, config):
        super().__init__("日常任务")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 添加调度设置
        self.scheduler_section = SchedulerSection(self.config, "daily_routine")
        layout.addWidget(self.scheduler_section)

        # 御魂配置
        harvest_group = QGroupBox("御魂配置")
        harvest_layout = QVBoxLayout(harvest_group)
        self.harvest_config = self.config["daily_routine"]["harvest_config"]

        self.enable_jade = QCheckBox("领取勾玉")
        self.enable_jade.setChecked(self.harvest_config["enable_jade"])
        harvest_layout.addWidget(self.enable_jade)

        self.enable_sign = QCheckBox("签到")
        self.enable_sign.setChecked(self.harvest_config["enable_sign"])
        harvest_layout.addWidget(self.enable_sign)

        self.enable_sign_999 = QCheckBox("签到999")
        self.enable_sign_999.setChecked(self.harvest_config["enable_sign_999"])
        harvest_layout.addWidget(self.enable_sign_999)

        self.enable_mail = QCheckBox("领取邮件")
        self.enable_mail.setChecked(self.harvest_config["enable_mail"])
        harvest_layout.addWidget(self.enable_mail)

        self.enable_soul = QCheckBox("领取御魂")
        self.enable_soul.setChecked(self.harvest_config["enable_soul"])
        harvest_layout.addWidget(self.enable_soul)

        self.enable_ap = QCheckBox("领取体力")
        self.enable_ap.setChecked(self.harvest_config["enable_ap"])
        harvest_layout.addWidget(self.enable_ap)

        layout.addWidget(harvest_group)

        # 杂项配置
        trifles_group = QGroupBox("杂项配置")
        trifles_layout = QVBoxLayout(trifles_group)
        self.trifles_config = self.config["daily_routine"]["trifles_config"]

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

    def update_config(self):
        self.scheduler_section.update_config()

        # 更新御魂配置
        self.harvest_config["enable_jade"] = self.enable_jade.isChecked()
        self.harvest_config["enable_sign"] = self.enable_sign.isChecked()
        self.harvest_config["enable_sign_999"] = self.enable_sign_999.isChecked()
        self.harvest_config["enable_mail"] = self.enable_mail.isChecked()
        self.harvest_config["enable_soul"] = self.enable_soul.isChecked()
        self.harvest_config["enable_ap"] = self.enable_ap.isChecked()

        # 更新杂项配置
        self.trifles_config["one_summon"] = self.one_summon.isChecked()
        self.trifles_config["guild_wish"] = self.guild_wish.isChecked()
        self.trifles_config["friend_love"] = self.friend_love.isChecked()
        self.trifles_config["store_sign"] = self.store_sign.isChecked()
