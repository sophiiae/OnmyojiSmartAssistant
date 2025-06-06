from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QComboBox, QLabel, QHBoxLayout

class WantedQuestsSection(QGroupBox):
    def __init__(self, config):
        super().__init__("悬赏任务设置")
        self.config = config
        layout = QVBoxLayout(self)
        accept = config["wanted_quests"]["accept_quest_config"]
        row = QHBoxLayout()
        row.addWidget(QLabel("接受任务类型:"))
        self.accept_type_combo = QComboBox()
        self.accept_type_combo.addItems(["勾玉", "金币", "体力", "御魂"])
        self.accept_type_combo.setCurrentText(accept.get("accept_type", "勾玉"))
        row.addWidget(self.accept_type_combo)
        layout.addLayout(row)

    def update_config(self):
        self.config["wanted_quests"]["accept_quest_config"]["accept_type"] = self.accept_type_combo.currentText()
