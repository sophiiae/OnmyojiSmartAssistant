from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox

class DailyRoutineSection(QGroupBox):
    def __init__(self, config):
        super().__init__("日常任务设置")
        self.config = config
        layout = QVBoxLayout(self)
        # 收获设置
        harvest = config["daily_routine"]["harvest_config"]
        self.enable_jade = QCheckBox("启用勾玉")
        self.enable_jade.setChecked(harvest.get("enable_jade", False))
        layout.addWidget(self.enable_jade)
        self.enable_sign = QCheckBox("启用签到")
        self.enable_sign.setChecked(harvest.get("enable_sign", False))
        layout.addWidget(self.enable_sign)
        self.enable_sign_999 = QCheckBox("启用999签到")
        self.enable_sign_999.setChecked(harvest.get("enable_sign_999", False))
        layout.addWidget(self.enable_sign_999)
        self.enable_mail = QCheckBox("启用邮件")
        self.enable_mail.setChecked(harvest.get("enable_mail", False))
        layout.addWidget(self.enable_mail)
        self.enable_soul = QCheckBox("启用御魂")
        self.enable_soul.setChecked(harvest.get("enable_soul", False))
        layout.addWidget(self.enable_soul)
        self.enable_ap = QCheckBox("启用体力")
        self.enable_ap.setChecked(harvest.get("enable_ap", False))
        layout.addWidget(self.enable_ap)
        # 杂项设置
        trifles = config["daily_routine"]["trifles_config"]
        self.one_summon = QCheckBox("一发召唤")
        self.one_summon.setChecked(trifles.get("one_summon", False))
        layout.addWidget(self.one_summon)
        self.guild_wish = QCheckBox("公会许愿")
        self.guild_wish.setChecked(trifles.get("guild_wish", False))
        layout.addWidget(self.guild_wish)
        self.friend_love = QCheckBox("好友赠送")
        self.friend_love.setChecked(trifles.get("friend_love", False))
        layout.addWidget(self.friend_love)
        self.store_sign = QCheckBox("商店签到")
        self.store_sign.setChecked(trifles.get("store_sign", False))
        layout.addWidget(self.store_sign)

    def update_config(self):
        self.config["daily_routine"]["harvest_config"]["enable_jade"] = self.enable_jade.isChecked()
        self.config["daily_routine"]["harvest_config"]["enable_sign"] = self.enable_sign.isChecked()
        self.config["daily_routine"]["harvest_config"]["enable_sign_999"] = self.enable_sign_999.isChecked()
        self.config["daily_routine"]["harvest_config"]["enable_mail"] = self.enable_mail.isChecked()
        self.config["daily_routine"]["harvest_config"]["enable_soul"] = self.enable_soul.isChecked()
        self.config["daily_routine"]["harvest_config"]["enable_ap"] = self.enable_ap.isChecked()
        self.config["daily_routine"]["trifles_config"]["one_summon"] = self.one_summon.isChecked()
        self.config["daily_routine"]["trifles_config"]["guild_wish"] = self.guild_wish.isChecked()
        self.config["daily_routine"]["trifles_config"]["friend_love"] = self.friend_love.isChecked()
        self.config["daily_routine"]["trifles_config"]["store_sign"] = self.store_sign.isChecked()
