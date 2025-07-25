from PyQt6.QtWidgets import QLineEdit, QLabel, QGroupBox, QVBoxLayout, QGridLayout, QCheckBox

class WantedQuestsSection(QGroupBox):
    def __init__(self, config):
        super().__init__("悬赏任务设置")
        self.config = config
        layout = QVBoxLayout(self)

        # 接受任务类型
        self.accept_quest_config = self.config["wanted_quests"]["accept_quest_config"]
        grid = QGridLayout()

        self.accept_jade = QCheckBox("勾玉悬赏")
        self.accept_jade.setChecked(self.accept_quest_config["accept_jade"])
        grid.addWidget(self.accept_jade, 0, 0)

        self.accept_gold = QCheckBox("金币悬赏")
        self.accept_gold.setChecked(self.accept_quest_config["accept_gold"])
        grid.addWidget(self.accept_gold, 0, 1)

        self.accept_ap = QCheckBox("体力悬赏")
        self.accept_ap.setChecked(self.accept_quest_config["accept_ap"])
        grid.addWidget(self.accept_ap, 0, 2)

        self.accept_virtual = QCheckBox("现世悬赏")
        self.accept_virtual.setChecked(
            self.accept_quest_config["accept_virtual"])
        grid.addWidget(self.accept_virtual, 1, 0)

        self.accept_pet_food = QCheckBox("宠物粮悬赏")
        self.accept_pet_food.setChecked(
            self.accept_quest_config["accept_pet_food"])
        grid.addWidget(self.accept_pet_food, 1, 1)

        group = QGroupBox("接受悬赏任务类型")
        group.setLayout(grid)
        layout.addWidget(group)

        # 邀请好友
        self.invite_quest_config = self.config["wanted_quests"]["invite_quest_config"]
        self.invite_friend_name = QLineEdit(
            self.invite_quest_config.get("invite_friend_name", ""))
        layout.addWidget(QLabel("邀请好友名称:"))
        layout.addWidget(self.invite_friend_name)

        # 邀请任务类型
        self.invite_quest_config = self.config["wanted_quests"]["invite_quest_config"]
        grid = QGridLayout()

        self.invite_jade = QCheckBox("勾玉悬赏")
        self.invite_jade.setChecked(self.invite_quest_config["invite_jade"])
        grid.addWidget(self.invite_jade, 0, 0)

        self.invite_gold = QCheckBox("金币悬赏")
        self.invite_gold.setChecked(self.invite_quest_config["invite_gold"])
        grid.addWidget(self.invite_gold, 0, 1)

        self.invite_ap = QCheckBox("体力悬赏")
        self.invite_ap.setChecked(self.invite_quest_config["invite_ap"])
        grid.addWidget(self.invite_ap, 0, 2)

        self.invite_virtual = QCheckBox("现世悬赏")
        self.invite_virtual.setChecked(
            self.invite_quest_config["invite_virtual"])
        grid.addWidget(self.invite_virtual, 1, 0)

        self.invite_food = QCheckBox("宠物粮悬赏")
        self.invite_food.setChecked(
            self.invite_quest_config["invite_pet_food"])
        grid.addWidget(self.invite_food, 1, 1)

        group = QGroupBox("邀请悬赏任务类型")
        group.setLayout(grid)
        layout.addWidget(group)

    def update_config(self):
        accept_quest_config = self.config["wanted_quests"]["accept_quest_config"]
        accept_quest_config["accept_jade"] = self.accept_jade.isChecked()
        accept_quest_config["accept_gold"] = self.accept_gold.isChecked()
        accept_quest_config["accept_ap"] = self.accept_ap.isChecked()
        accept_quest_config["accept_virtual"] = self.accept_virtual.isChecked()
        accept_quest_config["accept_pet_food"] = self.accept_pet_food.isChecked()

        invite_quest_config = self.config["wanted_quests"]["invite_quest_config"]
        invite_quest_config["invite_friend_name"] = self.invite_friend_name.text()
        invite_quest_config["invite_jade"] = self.invite_jade.isChecked()
        invite_quest_config["invite_gold"] = self.invite_gold.isChecked()
        invite_quest_config["invite_ap"] = self.invite_ap.isChecked()
        invite_quest_config["invite_virtual"] = self.invite_virtual.isChecked()
        invite_quest_config["invite_food"] = self.invite_food.isChecked()
        invite_quest_config["invite_friend_name"] = self.invite_friend_name.text()
