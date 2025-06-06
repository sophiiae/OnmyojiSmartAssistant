from PyQt6.QtWidgets import QHBoxLayout, QLabel

def add_labeled_widget(layout, label, widget):
    row = QHBoxLayout()
    row.addWidget(QLabel(label))
    row.addWidget(widget)
    layout.addLayout(row)
