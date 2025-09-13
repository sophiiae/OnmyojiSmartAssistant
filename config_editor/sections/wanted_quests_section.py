from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QGridLayout, QCheckBox

class WantedQuestsSection(QGroupBox):
    def __init__(self, config):
        super().__init__("悬赏任务")
        self.config = config
        layout = QVBoxLayout(self)

        # 接受任务类型
        self.accept_quest_config = self.config["wanted_quests"]["accept_quest_config"]
        grid = QGridLayout()

        self.accept_jade = QCheckBox("勾玉悬赏")
        self.accept_jade.setChecked(self.accept_quest_config["accept_jade"])
        grid.addWidget(self.accept_jade, 0, 0)

        self.accept_ap = QCheckBox("体力悬赏")
        self.accept_ap.setChecked(self.accept_quest_config["accept_ap"])
        grid.addWidget(self.accept_ap, 0, 1)

        self.accept_pet_food = QCheckBox("宠物粮悬赏")
        self.accept_pet_food.setChecked(
            self.accept_quest_config["accept_pet_food"])
        grid.addWidget(self.accept_pet_food, 0, 2)

        group = QGroupBox("接受悬赏任务类型")
        group.setLayout(grid)
        layout.addWidget(group)

    def update_config(self):
        accept_quest_config = self.config["wanted_quests"]["accept_quest_config"]
        accept_quest_config["accept_jade"] = self.accept_jade.isChecked()
        accept_quest_config["accept_ap"] = self.accept_ap.isChecked()
        accept_quest_config["accept_pet_food"] = self.accept_pet_food.isChecked()
