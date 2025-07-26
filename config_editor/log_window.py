from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton,
                             QHBoxLayout, QLabel, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat
import sys
import io
import threading
from datetime import datetime
import queue
import logging
import re


class LogWindow(QWidget):
    """日志显示窗口 - 内嵌版本"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.run_button = None  # 运行按钮引用
        self.setup_ui()

    def set_run_button(self, run_button):
        """设置运行按钮"""
        self.run_button = run_button
        # 将运行按钮添加到控制栏
        if self.run_button:
            # 移除按钮的父级，避免重复添加
            if self.run_button.parent():
                self.run_button.setParent(None)
            # 将按钮添加到控制栏的左侧
            self.control_layout.insertWidget(0, self.run_button)

    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 顶部控制栏
        self.control_layout = QHBoxLayout()

        # 清空日志按钮
        self.clear_button = QPushButton("清空")
        self.clear_button.setMaximumWidth(60)
        self.clear_button.setStyleSheet("""
            QPushButton {
                padding: 3px 8px;
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 3px;
                color: #D32F2F;
                background-color: #f8f8f8;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.clear_button.clicked.connect(self.clear_log)
        self.control_layout.addStretch()
        self.control_layout.addWidget(self.clear_button)

        layout.addLayout(self.control_layout)

        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.log_text)

        # 底部信息栏
        info_layout = QHBoxLayout()
        self.line_count_label = QLabel("行数: 0")
        self.line_count_label.setStyleSheet("font-size: 11px; color: #666;")
        info_layout.addWidget(self.line_count_label)

        info_layout.addStretch()

        self.timestamp_label = QLabel("")
        self.timestamp_label.setStyleSheet("font-size: 11px; color: #666;")
        info_layout.addWidget(self.timestamp_label)

        layout.addLayout(info_layout)

        # 定时器用于更新状态
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(1000)  # 每秒更新一次

    def start_log_capture(self):
        """开始日志捕获 - 设置UI回调"""
        # 设置logger的UI回调
        from module.base.logger import logger
        logger.set_ui_callback(self.append_log)

    def stop_log_capture(self):
        """停止日志捕获 - 清除UI回调"""
        # 清除logger的UI回调
        from module.base.logger import logger
        logger.set_ui_callback(None)

        # 添加停止分割线
        self.append_stop_separator()

    def append_stop_separator(self):
        """添加停止分割线"""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # 创建红色分割线格式
        separator_format = QTextCharFormat()
        separator_format.setForeground(QColor('#F44336'))  # 红色

        # 添加分割线
        separator_text = "─" * 27 + " 脚本已停止 " + "─" * 27 + "\n"
        cursor.insertText(separator_text, separator_format)

        # 自动滚动到底部
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def append_log(self, text):
        """添加日志文本"""
        # 创建带颜色的文本格式
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # 根据日志内容设置颜色
        color_format = self.get_log_color_format(text)
        cursor.insertText(text + "\n", color_format)

        # 自动滚动到底部
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def get_log_color_format(self, text):
        """根据日志内容获取颜色格式"""
        format = QTextCharFormat()

        # 定义颜色映射
        colors = {
            'INFO': QColor('#4CAF50'),      # 绿色
            'WARNING': QColor('#FF9800'),   # 橙色
            'ERROR': QColor('#F44336'),     # 红色
            'CRITICAL': QColor('#D32F2F'),  # 深红色
            'SUCCESS': QColor('#8BC34A'),   # 浅绿色
            'DEBUG': QColor('#00BCD4'),     # 青色
            'SYSTEM': QColor('#2196F3'),    # 蓝色
            'NETWORK': QColor('#9C27B0'),   # 紫色
            'AI': QColor('#00BCD4'),        # 青色
            'BACKGROUND': QColor('#757575')  # 灰色
        }

        # 默认颜色
        default_color = QColor('#FFFFFF')  # 白色

        # 根据文本内容判断日志类型
        if 'ℹ️' in text or '[INFO]' in text:
            format.setForeground(colors['INFO'])
        elif '⚠️' in text or '[WARNING]' in text:
            format.setForeground(colors['WARNING'])
        elif '❌' in text or '[ERROR]' in text:
            format.setForeground(colors['ERROR'])
        elif '💥' in text or '[CRITICAL]' in text:
            format.setForeground(colors['CRITICAL'])
        elif '✅' in text or '[SUCCESS]' in text:
            format.setForeground(colors['SUCCESS'])
        elif '🐛' in text or '[DEBUG]' in text:
            format.setForeground(colors['DEBUG'])
        elif '🖥️' in text or '[SYSTEM]' in text:
            format.setForeground(colors['SYSTEM'])
        elif '🌐' in text or '[NETWORK]' in text:
            format.setForeground(colors['NETWORK'])
        elif '🤖' in text or '[AI]' in text:
            format.setForeground(colors['AI'])
        elif '[BG]' in text or '[BACKGROUND]' in text:
            format.setForeground(colors['BACKGROUND'])
        else:
            format.setForeground(default_color)

        return format

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()

    def update_info(self):
        """更新信息栏"""
        # 更新行数
        document = self.log_text.document()
        if document:
            line_count = document.lineCount()
            self.line_count_label.setText(f"行数: {line_count}")

        # # 更新时间戳
        # current_time = datetime.now().strftime("%H:%M:%S")
        # self.timestamp_label.setText(f"更新: {current_time}")
