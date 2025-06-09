from PyQt6.QtWidgets import QPushButton, QComboBox, QDialog, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal

class ValueSelectDialog(QDialog):
    def __init__(self, items, current_index, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择选项")
        self.setMinimumSize(160, 100)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 创建ComboBox
        self.combobox = QComboBox()
        self.combobox.addItems(items)
        self.combobox.setCurrentIndex(current_index)
        layout.addWidget(self.combobox)

        # 按钮布局
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # 连接信号
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

class SelectButton(QPushButton):
    currentIndexChanged = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._items = []
        self._current_index = 0
        self.setStyleSheet("""
            QPushButton {
                padding: 2px 4px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #f5f5f5;
                color: #333;
                text-align: center;
            }
            QPushButton:hover {
                background: #e0e0e0;
                border-color: #2196F3;
            }
        """)
        self.setText("请选择")  # 默认显示文本
        self.clicked.connect(self.show_dialog)
        self.setSizePolicy(QSizePolicy.Policy.Preferred,
                           QSizePolicy.Policy.Fixed)

    def addItems(self, items):
        self._items = items
        if items:
            self.setText(items[0])

    def setCurrentIndex(self, index):
        if 0 <= index < len(self._items):
            self._current_index = index
            self.setText(self._items[index])

    def currentIndex(self):
        return self._current_index

    def setCurrentText(self, text):
        if text in self._items:
            index = self._items.index(text)
            self.setCurrentIndex(index)

    def currentText(self):
        return self._items[self._current_index] if self._items else ""

    def show_dialog(self):
        dialog = ValueSelectDialog(self._items, self._current_index, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_index = dialog.combobox.currentIndex()
            if new_index != self._current_index:
                self.setCurrentIndex(new_index)
                self.currentIndexChanged.emit(new_index)
