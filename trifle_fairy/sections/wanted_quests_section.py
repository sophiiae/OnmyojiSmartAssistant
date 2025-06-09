from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit
from trifle_fairy.sections.script_section import add_labeled_widget
from config_editor.widgets.select_button import SelectButton

class WantedQuestsSection(QGroupBox):
    def __init__(self, config):
        super().__init__("悬赏任务设置")
        self.config = config
        layout = QVBoxLayout(self)
        quest_config = config["wanted_quests"]

        accept_edit = QHBoxLayout()
        accept_edit.addWidget(QLabel("接受任务类型:"))
        self.accept_type_combo = SelectButton()
        self.accept_type_combo.addItems(["勾玉", "金币", "体力", "御魂"])
        self.accept_type_combo.setCurrentText(
            quest_config.get("accept_type", "勾玉"))
        accept_edit.addWidget(self.accept_type_combo)
        layout.addLayout(accept_edit)

        invite_edit = QHBoxLayout()
        invite_edit.addWidget(QLabel("邀请任务类型:"))
        self.invite_type_combo = SelectButton()
        self.invite_type_combo.addItems(["勾玉", "金币", "体力", "御魂"])
        self.invite_type_combo.setCurrentText(
            quest_config.get("invite_type", "勾玉"))
        invite_edit.addWidget(self.invite_type_combo)
        layout.addLayout(invite_edit)

        self.friend_name = QLineEdit(
            str(quest_config.get("invite_friend_name", "")))
        add_labeled_widget(layout, "邀请好友名字", self.friend_name)

    def update_config(self):
        quest_config = self.config["wanted_quests"]
        quest_config["accept_type"] = self.accept_type_combo.currentText()
        quest_config["invite_type"] = self.invite_type_combo.currentText()
        quest_config["invite_friend_name"] = self.friend_name.text()
