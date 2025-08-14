from PyQt6.QtWidgets import QPushButton, QSpinBox, QDialog, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

class ValueEditDialog(QDialog):
    def __init__(self, value, min_value, max_value, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改数值")
        self.setMinimumSize(160, 100)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 创建SpinBox
        self.spinbox = QSpinBox()
        self.spinbox.setRange(min_value, max_value)
        self.spinbox.setValue(value)
        layout.addWidget(self.spinbox)

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

class ValueButton(QPushButton):
    valueChanged = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = 0
        self._min_value = 0
        self._max_value = 99
        self.setStyleSheet("""
            QPushButton {
                padding: 3px 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #f5f5f5;
                color: #333;
                min-width: 80px;
                text-align: center;
            }
            QPushButton:hover {
                background: #e0e0e0;
                border-color: #2196F3;
            }
        """)
        self.setText("0")  # 默认显示0
        self.clicked.connect(self.show_dialog)

    def setRange(self, min_value, max_value):
        self._min_value = min_value
        self._max_value = max_value

    def setValue(self, value):
        self._value = value
        self.setText(str(value))

    def value(self):
        return self._value

    def show_dialog(self):
        dialog = ValueEditDialog(
            self._value, self._min_value, self._max_value, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_value = dialog.spinbox.value()
            if new_value != self._value:
                self.setValue(new_value)
                self.valueChanged.emit(new_value)
