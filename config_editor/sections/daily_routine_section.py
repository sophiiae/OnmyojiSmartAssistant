from PyQt6.QtWidgets import (QVBoxLayout, QCheckBox, QGroupBox, QGridLayout)
from config_editor.sections.scheduler_section import SchedulerSection

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
        self.harvest_config = self.config["daily_routine"]["harvest_config"]
        grid = QGridLayout()

        self.enable_sign = QCheckBox("签到")
        self.enable_sign.setChecked(self.harvest_config["enable_sign"])
        grid.addWidget(self.enable_sign, 0, 0)

        self.enable_sign_999 = QCheckBox("签到999")
        self.enable_sign_999.setChecked(self.harvest_config["enable_sign_999"])
        grid.addWidget(self.enable_sign_999, 0, 1)

        self.enable_mail = QCheckBox("领取邮件")
        self.enable_mail.setChecked(self.harvest_config["enable_mail"])
        grid.addWidget(self.enable_mail, 0, 2)

        self.enable_soul = QCheckBox("领取御魂")
        self.enable_soul.setChecked(self.harvest_config["enable_soul"])
        grid.addWidget(self.enable_soul, 1, 0)

        self.enable_jade = QCheckBox("领取勾玉")
        self.enable_jade.setChecked(self.harvest_config["enable_jade"])
        grid.addWidget(self.enable_jade, 1, 1)

        self.enable_ap = QCheckBox("领取体力")
        self.enable_ap.setChecked(self.harvest_config["enable_ap"])
        grid.addWidget(self.enable_ap, 1, 2)

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

    def update_config(self):
        self.scheduler_section.update_config()

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

    def refresh_from_config(self, config):
        """根据配置刷新UI控件"""
        try:
            # 更新内部配置引用
            self.config = config
            daily_config = config["daily_routine"]

            # 刷新scheduler section
            if hasattr(self, 'scheduler_section'):
                self.scheduler_section.refresh_from_config(config)

        except Exception as e:
            from module.base.logger import logger
            logger.error(f"刷新日常任务设置UI时出错: {e}")
