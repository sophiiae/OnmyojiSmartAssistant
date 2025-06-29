from PyQt6.QtWidgets import (QDialog, QPushButton, QGroupBox, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QLabel, QListWidget)
from PyQt6.QtCore import Qt
from config_editor.utils import add_labeled_widget

class RegionsDialog(QDialog):
    def __init__(self, region="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑副设备")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 添加输入框
        self.region_edit = QLineEdit(region)
        layout.addWidget(QLabel("账号区服:"))
        layout.addWidget(self.region_edit)

        # 添加按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setMinimumWidth(300)

class ScriptSection(QGroupBox):
    def __init__(self, config):
        super().__init__("脚本设置")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        script_config = self.config["script"]

        # 设备设置
        device = script_config["device"]
        self.serial_edit = QLineEdit(str(device.get("serial", "")))
        add_labeled_widget(layout, "设备序列号", self.serial_edit)

        # 账号区域设置
        subhost_layout = QVBoxLayout()
        subhost_layout.addWidget(QLabel("账号区服列表: (第一个为默认区服)"))

        # 创建列表控件
        self.subhost_list = QListWidget()
        self.subhost_list.setMinimumHeight(100)
        self.subhost_list.setSizeAdjustPolicy(
            QListWidget.SizeAdjustPolicy.AdjustToContents)
        self.subhost_list.addItems(script_config.get("regions", []))
        subhost_layout.addWidget(self.subhost_list)

        # 添加按钮布局
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("添加")
        self.edit_button = QPushButton("编辑")
        self.remove_button = QPushButton("删除")

        self.add_button.clicked.connect(self.add_region)
        self.edit_button.clicked.connect(self.edit_region)
        self.remove_button.clicked.connect(self.remove_subhost)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        subhost_layout.addLayout(button_layout)

        layout.addLayout(subhost_layout)

    def add_region(self):
        dialog = RegionsDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_subhost = dialog.region_edit.text().strip()
            if new_subhost:
                self.subhost_list.addItem(new_subhost)

    def edit_region(self):
        current_item = self.subhost_list.currentItem()
        if current_item:
            dialog = RegionsDialog(current_item.text(), parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_subhost = dialog.region_edit.text().strip()
                if new_subhost:
                    current_item.setText(new_subhost)

    def remove_subhost(self):
        current_item = self.subhost_list.currentItem()
        if current_item:
            self.subhost_list.takeItem(self.subhost_list.row(current_item))

    def update_config(self):
        script_config = self.config["script"]
        script_config["device"]["serial"] = self.serial_edit.text()
        script_config["regions"] = [item.text() for item in self.subhost_list.findItems(
            "", Qt.MatchFlag.MatchContains)]
