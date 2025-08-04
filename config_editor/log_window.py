from pathlib import Path
from datetime import datetime
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton,
                             QHBoxLayout, QLabel, QCheckBox)
from module.control.server.data_collector import DataCollector
import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = Path(__file__).parent.parent

# 数据相关配置
DATA_DIR = PROJECT_ROOT / "data"
VIDEOS_DIR = DATA_DIR / "videos"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"

class LogSignals(QObject):
    """日志信号类"""
    log_message = pyqtSignal(str)

class LogWindow(QWidget):
    """日志显示窗口 - 内嵌版本"""

    def __init__(self, config_name: str):
        super().__init__()  # 调用父类的__init__方法
        self.run_button = None  # 运行按钮引用
        self.config_name = config_name
        self.device = None  # 延迟初始化设备
        self.device_connected = False  # 设备连接状态
        self.is_recording = False  # 录制状态

        # 创建信号对象
        self.signals = LogSignals()
        self.signals.log_message.connect(self.append_log_safe)

        # 不再自动初始化设备，等待用户手动选择
        self.setup_ui()

    def set_active(self, active: bool):
        """设置日志窗口的活动状态 - 现在只是注册/注销回调"""
        if active:
            # 激活时，注册UI回调，传入配置名称
            self.start_log_capture()

    def append_log_safe(self, text):
        """线程安全的日志添加方法"""
        try:
            # 创建带颜色的文本格式
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)

            # 根据日志内容设置颜色
            color_format = self.get_log_color_format(text)
            cursor.insertText(text + "\n", color_format)

            # 自动滚动到底部
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
        except Exception as e:
            # 如果UI更新失败，至少打印到控制台
            print(f"Log UI update failed: {e}")

    def init_device(self):
        """异步初始化设备连接"""
        try:
            self.device = DataCollector(self.config_name)
            # 检查设备是否成功连接
            if self.device.device is not None:
                self.device_connected = True
                self.screenshot_button.setEnabled(True)
                self.record_button.setEnabled(True)
                self.update_button_styles()
                self.append_log("✅ 设备连接成功")
            else:
                self.device_connected = False
                self.screenshot_button.setEnabled(False)
                self.record_button.setEnabled(False)
                self.update_button_styles()
                self.append_log("❌ 设备连接失败，截图和录屏功能已禁用")
        except Exception as e:
            self.device_connected = False
            self.screenshot_button.setEnabled(False)
            self.record_button.setEnabled(False)
            self.update_button_styles()
            self.append_log(f"❌ 设备初始化失败: {str(e)}，截图和录屏功能已禁用")

    def on_device_checkbox_changed(self, state):
        """处理设备连接复选框状态改变"""
        if state == 2:  # Qt.Checked
            self.append_log("🔄 正在连接设备...")
            self.init_device()
        else:  # Qt.Unchecked
            self.device_connected = False
            self.screenshot_button.setEnabled(False)
            self.device = None
            self.append_log("📱 已断开设备连接")
            self.update_button_styles()

    def update_button_styles(self):
        """根据设备连接状态更新按钮样式"""
        if self.device_connected:
            # 连接成功时的样式 - 蓝色
            self.screenshot_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 8px;
                    font-size: 12px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    color: #219ebc;
                    background-color: #f8f8f8;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            # 录屏按钮 - 粉色
            self.record_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 8px;
                    font-size: 12px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    color: #e91e63;
                    background-color: #f8f8f8;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
        else:
            # 未连接时的样式 - 灰色
            self.screenshot_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 8px;
                    font-size: 12px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    color: #999999;
                    background-color: #f5f5f5;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            self.record_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 8px;
                    font-size: 12px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    color: #999999;
                    background-color: #f5f5f5;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

    def update_screenshot_button_style(self):
        """根据设备连接状态更新截图按钮样式"""
        if self.device_connected:
            # 连接成功时的样式 - 蓝色
            self.screenshot_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 8px;
                    font-size: 12px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    color: #219ebc;
                    background-color: #f8f8f8;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
        else:
            # 未连接时的样式 - 灰色
            self.screenshot_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 8px;
                    font-size: 12px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    color: #999999;
                    background-color: #f5f5f5;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

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
        # 主布局
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
                border: 1px solid #b5bdc4;
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

        # 设备连接复选框
        self.device_checkbox = QCheckBox("连接设备")
        self.device_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 11px;
                color: #666;
                padding: 0 10px 0 0;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
        """)
        self.device_checkbox.stateChanged.connect(
            self.on_device_checkbox_changed)
        info_layout.addWidget(self.device_checkbox)

        # 截图按钮
        self.screenshot_button = QPushButton("截图")
        self.screenshot_button.setMaximumWidth(60)
        self.screenshot_button.setStyleSheet("""
            QPushButton {
                padding: 3px 8px;
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 3px;
                color: #219ebc;
                background-color: #f8f8f8;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.screenshot_button.clicked.connect(self.capture_screenshot)
        self.screenshot_button.setEnabled(False)  # 初始时禁用截图按钮
        info_layout.addWidget(self.screenshot_button)

        # 录屏按钮
        self.record_button = QPushButton("录屏")
        self.record_button.setMaximumWidth(60)
        self.record_button.setStyleSheet("""
            QPushButton {
                padding: 3px 8px;
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 3px;
                color: #e91e63;
                background-color: #f8f8f8;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setEnabled(False)  # 初始时禁用录屏按钮
        info_layout.addWidget(self.record_button)

        self.update_button_styles()  # 设置初始样式

        layout.addLayout(info_layout)

        # 定时器用于更新状态
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(1000)  # 每秒更新一次

    def start_log_capture(self):
        """开始日志捕获 - 注册UI回调，传入配置名称"""
        # 注册logger的UI回调，传入配置名称
        from module.base.logger import logger
        logger.set_ui_callback(self.append_log, self.config_name)

    def stop_log_capture(self):
        """停止日志捕获 - 注销UI回调"""
        # 注销logger的UI回调
        from module.base.logger import logger
        logger.remove_ui_callback(self.append_log)

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
        """添加日志文本 - 使用信号槽机制"""
        # 使用信号槽机制，避免阻塞UI线程
        self.signals.log_message.emit(text)

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

    def capture_screenshot(self):
        """截图"""
        if not self.device_connected or self.device is None:
            self.append_log("❌ 设备未连接，无法截图")
            return

        # 确保目录存在
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = SCREENSHOTS_DIR / f"{timestamp}.cap.png"

        try:
            success = self.device.capture_screenshot(output_path)
            if success:
                self.append_log(f"✅ 截图已保存: {output_path}")
            else:
                self.append_log("❌ 截图失败")
        except Exception as e:
            self.append_log(f"❌ 截图失败: {str(e)}")

    def toggle_recording(self):
        """切换录屏状态"""
        if not self.device_connected:
            self.append_log("❌ 设备未连接，无法录制视频")
            return

        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """开始录制视频"""
        try:
            if self.device is None:
                self.append_log("❌ 数据收集器未初始化")
                return

            # 确保目录存在
            VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.recording_path = VIDEOS_DIR / f"recording_{timestamp}.mp4"

            # 调用data_collector开始录制
            if self.device.start_recording(self.recording_path):
                self.is_recording = True
                self.record_button.setText("停止")
                self.record_button.setStyleSheet("""
                    QPushButton {
                        padding: 3px 8px;
                        font-size: 12px;
                        border: 1px solid #ccc;
                        border-radius: 3px;
                        color: white;
                        background-color: #f44336;
                    }
                    QPushButton:hover {
                        background-color: #d32f2f;
                    }
                """)
                self.append_log("🎬 开始录制视频...")
                self.append_log("💡 提示：录制将持续到您点击停止按钮")
            else:
                self.append_log("❌ 开始录制失败")

        except Exception as e:
            self.append_log(f"❌ 开始录制失败: {str(e)}")
            self.is_recording = False

    def stop_recording(self):
        """停止录制视频"""
        try:
            if self.device is None:
                self.append_log("❌ 数据收集器未初始化")
                return

            self.is_recording = False
            self.record_button.setText("录屏")
            self.update_button_styles()
            self.append_log("⏹️ 正在停止录制...")

            # 调用device停止录制
            if self.device.stop_recording():
                self.append_log("✅ 录制已停止")
                self.append_log(f"📁 视频文件已保存到: {self.recording_path}")
            else:
                self.append_log("❌ 停止录制失败")
                self.append_log("💡 提示：录制时间可能太短，请尝试录制更长时间")

        except Exception as e:
            self.append_log(f"❌ 停止录制失败: {str(e)}")
