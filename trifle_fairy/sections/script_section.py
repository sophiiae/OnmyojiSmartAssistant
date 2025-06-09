from PyQt6.QtWidgets import (QCheckBox, QComboBox, QGroupBox, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QListWidget, QMessageBox)
from PyQt6.QtCore import Qt
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton

def add_labeled_widget(layout, label_text, widget):
    row = QHBoxLayout()
    row.addWidget(QLabel(label_text))
    row.addWidget(widget)
    layout.addLayout(row)

class SubhostDialog(QDialog):
    def __init__(self, subhost="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑副设备")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 添加输入框
        self.subhost_edit = QLineEdit(subhost)
        layout.addWidget(QLabel("副设备序列号:"))
        layout.addWidget(self.subhost_edit)

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
        self.config = config["script"]
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 设备设置
        self.serial_edit = QLineEdit(str(self.config.get("main_host", "")))
        add_labeled_widget(layout, "主设备序列号", self.serial_edit)

        # 副设备列表
        subhost_layout = QVBoxLayout()
        subhost_layout.addWidget(QLabel("副设备端口列表:"))

        # 创建列表控件
        self.subhost_list = QListWidget()
        self.subhost_list.setMinimumHeight(100)
        self.subhost_list.setSizeAdjustPolicy(
            QListWidget.SizeAdjustPolicy.AdjustToContents)
        self.subhost_list.addItems(self.config.get("subhosts", []))
        subhost_layout.addWidget(self.subhost_list)

        # 添加按钮布局
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("添加")
        self.edit_button = QPushButton("编辑")
        self.remove_button = QPushButton("删除")

        self.add_button.clicked.connect(self.add_subhost)
        self.edit_button.clicked.connect(self.edit_subhost)
        self.remove_button.clicked.connect(self.remove_subhost)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        subhost_layout.addLayout(button_layout)

        layout.addLayout(subhost_layout)

    def add_subhost(self):
        dialog = SubhostDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_subhost = dialog.subhost_edit.text().strip()
            if new_subhost:
                self.subhost_list.addItem(new_subhost)

    def edit_subhost(self):
        current_item = self.subhost_list.currentItem()
        if current_item:
            dialog = SubhostDialog(current_item.text(), parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_subhost = dialog.subhost_edit.text().strip()
                if new_subhost:
                    current_item.setText(new_subhost)

    def remove_subhost(self):
        current_item = self.subhost_list.currentItem()
        if current_item:
            self.subhost_list.takeItem(self.subhost_list.row(current_item))

    def update_config(self):
        self.config["main_host"] = self.serial_edit.text()
        self.config["subhosts"] = [item.text() for item in self.subhost_list.findItems(
            "", Qt.MatchFlag.MatchContains)]
