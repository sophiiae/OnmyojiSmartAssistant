from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                             QWidget, QScrollArea, QCheckBox, QComboBox, QSpinBox, QLineEdit,
                             QPushButton, QHBoxLayout, QMessageBox, QLabel, QGridLayout)
import os
import sys
from PyQt6.QtCore import Qt
from config_editor.sections.script_section import ScriptSection
from config_editor.sections.daily_routine_section import DailyRoutineSection
from config_editor.sections.wanted_quests_section import WantedQuestsSection
from config_editor.sections.exploration_section import ExplorationSection
from config_editor.sections.realm_raid_section import RealmRaidSection
from config_editor.sections.goryou_realm_section import GoryouRealmSection
from config_editor.sections.shikigami_activity_section import ShikigamiActivitySection
from config_editor.sections.area_boss_section import AreaBossSection
from config_editor.main import ConfigTab
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton
from PyQt6.QtWidgets import QTabWidget
from config_editor.script_worker import ScriptWorker
from config_editor.log_window import LogWindow

CONFIG_DIR = "configs"

class OSAEditor(ConfigTab):
    def __init__(self, config_path):
        super().__init__(config_path)
        self.setWindowTitle("OSA 配置编辑器")
        self.script_worker = None
        self.log_window = None
        self.setup_ui()

    def setup_ui(self):
        """设置UI界面"""
        # 主布局 - 使用水平布局来放置配置区域和日志区域
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)

        # 左侧配置区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 创建运行按钮（将移到日志窗口内部）
        self.run_button = QPushButton("运行")
        self.run_button.setMinimumWidth(80)  # 设置最小宽度，类似状态标签
        self.run_button.setMaximumWidth(100)  # 设置最大宽度
        self.run_button.setStyleSheet("""
            QPushButton {
                padding: 3px 8px;
                border-radius: 3px;
                background-color: #2196F3;
                color: white;
                font-size: 12px;
                border: 1px solid #1976D2;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.run_button.clicked.connect(self.run_osa_config)

        # 快速导航栏
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)

        # 导航标题
        nav_title = QLabel("快速导航:")
        nav_layout.addWidget(nav_title)

        # 创建按钮容器，使用网格布局实现自动换行
        button_container = QWidget()
        button_layout = QGridLayout(button_container)
        button_layout.setSpacing(5)  # 设置按钮间距

        # 创建导航按钮
        sections = [
            ("script", "脚本设置", None),  # 脚本设置没有启用状态
            ("daily_routine", "日常任务", "daily_routine.scheduler.enable"),
            ("wanted_quests", "悬赏任务", None),  # 悬赏任务没有启用状态
            ("exploration", "探索", "exploration.scheduler.enable"),
            ("realm_raid", "结界突破", "realm_raid.scheduler.enable"),
            ("goryou_realm", "御灵", "goryou_realm.scheduler.enable"),
            ("shikigami_activity", "式神活动", "shikigami_activity.scheduler.enable"),
            ("area_boss", "地域鬼王", "area_boss.scheduler.enable")
        ]

        # 设置统一的按钮样式
        button_style = """
            QPushButton {
                min-width: 45px;
                max-width: 55px;
                font-size: 9px;
                margin: 1px;
            }
        """

        # 计算每行最多放置的按钮数量（根据容器宽度动态调整）
        max_buttons_per_row = 7  # 增加到7个按钮一行，更紧凑

        for i, (section_id, section_name, enable_path) in enumerate(sections):
            btn = QPushButton(section_name)
            btn.setStyleSheet(button_style)  # 应用基础样式
            btn.clicked.connect(
                lambda checked, s=section_id: self.scroll_to_section(s))

            # 计算按钮在网格中的位置
            row = i // max_buttons_per_row
            col = i % max_buttons_per_row

            button_layout.addWidget(btn, row, col)
            self.nav_buttons[section_id] = (btn, enable_path)

        nav_layout.addWidget(button_container)
        left_layout.addWidget(nav_widget)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 禁用水平滚动条
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # 只在需要时显示垂直滚动条

        # 创建滚动区域的内容部件
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)  # 设置部件之间的间距
        scroll_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距

        # 添加所有配置部分
        self.script_section = ScriptSection(self.config)
        scroll_layout.addWidget(self.script_section)
        self.daily_routine_section = DailyRoutineSection(self.config)
        scroll_layout.addWidget(self.daily_routine_section)
        self.wanted_quests_section = WantedQuestsSection(self.config)
        scroll_layout.addWidget(self.wanted_quests_section)
        self.exploration_section = ExplorationSection(self.config)
        scroll_layout.addWidget(self.exploration_section)
        self.realm_raid_section = RealmRaidSection(self.config)
        scroll_layout.addWidget(self.realm_raid_section)
        self.goryou_realm_section = GoryouRealmSection(self.config)
        scroll_layout.addWidget(self.goryou_realm_section)
        self.shikigami_activity_section = ShikigamiActivitySection(self.config)
        scroll_layout.addWidget(self.shikigami_activity_section)
        self.area_boss_section = AreaBossSection(self.config)
        scroll_layout.addWidget(self.area_boss_section)

        # 添加弹性空间，使内容靠上
        scroll_layout.addStretch()

        # 设置滚动区域的内容
        scroll.setWidget(scroll_widget)
        left_layout.addWidget(scroll)

        # 自动保存
        self.install_auto_save()

        # 更新导航按钮状态
        self.update_nav_buttons()

        # 设置左侧配置区域的固定宽度
        left_widget.setMinimumWidth(800)  # 缩小左侧宽度
        left_widget.setMaximumWidth(450)  # 设置最大宽度

        # 添加左侧配置区域到主布局
        main_layout.addWidget(left_widget)

        # 右侧日志区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 创建内嵌的日志窗口，并将运行按钮传递给它
        self.log_window = LogWindow()
        self.log_window.setParent(right_widget)
        self.log_window.set_run_button(self.run_button)  # 传递运行按钮给日志窗口
        right_layout.addWidget(self.log_window)

        # 设置右侧日志区域的固定宽度
        right_widget.setMinimumWidth(500)  # 扩大右侧宽度

        # 添加右侧日志区域到主布局
        main_layout.addWidget(right_widget)

    def closeEvent(self, a0):
        """窗口关闭时的处理"""
        if self.script_worker and self.script_worker.isRunning():
            self.script_worker.terminate()
            self.script_worker.wait()

        # 停止日志捕获
        if self.log_window:
            self.log_window.stop_log_capture()

        if a0:
            a0.accept()
        super().closeEvent(a0)

    def save_osa_config(self):
        self.script_section.update_config()
        self.daily_routine_section.update_config()
        self.wanted_quests_section.update_config()
        self.exploration_section.update_config()
        self.realm_raid_section.update_config()
        self.goryou_realm_section.update_config()
        self.shikigami_activity_section.update_config()
        self.area_boss_section.update_config()
        self.save_config()

    def run_osa_config(self):
        """运行当前配置"""
        try:
            if not self.is_running:
                # 保存当前配置
                self.save_osa_config()

                # 获取配置名称（文件名去掉.json后缀）
                config_name = os.path.splitext(
                    os.path.basename(self.config_path))[0]

                # 创建工作线程
                self.script_worker = ScriptWorker(config_name, self.log_window)
                self.script_worker.finished.connect(self.on_script_finished)
                self.script_worker.error.connect(self.on_script_error)

                # 启动线程
                self.script_worker.start()

                # 更新UI状态
                self.is_running = True
                self.update_run_button()
                # QMessageBox.information(
                #     self, "成功", f"配置 {config_name} 已开始运行")
            else:
                # 停止脚本
                self.stop_script()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"运行配置时出错: {str(e)}")

    def stop_script(self):
        """停止脚本运行"""
        if self.script_worker and self.script_worker.isRunning():
            self.script_worker.terminate()
            self.script_worker.wait()

        # 停止日志捕获
        if self.log_window:
            self.log_window.stop_log_capture()

        self.is_running = False
        self.update_run_button()
        # QMessageBox.information(self, "成功", "配置已停止运行")

    def on_script_finished(self):
        """脚本完成时的回调"""
        # 停止日志捕获
        if self.log_window:
            self.log_window.stop_log_capture()

        self.is_running = False
        self.update_run_button()
        self.script_worker = None

    def on_script_error(self, error_msg):
        """脚本出错时的回调"""
        # 停止日志捕获
        if self.log_window:
            self.log_window.stop_log_capture()

        self.is_running = False
        self.update_run_button()
        self.script_worker = None
        QMessageBox.critical(self, "错误", f"脚本运行出错: {error_msg}")

    def update_run_button(self):
        """更新运行按钮的样式和文本"""
        if self.is_running:
            self.run_button.setText("停止")
            self.run_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 8px;
                    border-radius: 3px;
                    background-color: #f44336;
                    color: white;
                    font-size: 12px;
                    border: 1px solid #d32f2f;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
        else:
            self.run_button.setText("运行")
            self.run_button.setStyleSheet("""
                QPushButton {
                    padding: 3px 8px;
                    border-radius: 3px;
                    background-color: #2196F3;
                    color: white;
                    font-size: 12px;
                    border: 1px solid #1976D2;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)

    def install_auto_save(self):
        # 给所有控件加信号，内容变动时自动保存
        for section in [self.script_section, self.daily_routine_section, self.wanted_quests_section,
                        self.exploration_section, self.realm_raid_section, self.goryou_realm_section,
                        self.shikigami_activity_section, self.area_boss_section]:
            for child in section.findChildren((QCheckBox, QComboBox, QSpinBox, QLineEdit, ValueButton, SelectButton)):
                if hasattr(child, 'textChanged'):
                    child.textChanged.connect(self.on_config_changed)
                if hasattr(child, 'currentIndexChanged'):
                    child.currentIndexChanged.connect(self.on_config_changed)
                if hasattr(child, 'stateChanged'):
                    child.stateChanged.connect(self.on_config_changed)
                if hasattr(child, 'valueChanged'):
                    child.valueChanged.connect(self.on_config_changed)

    def on_config_changed(self):
        """配置改变时的处理函数"""
        self.save_osa_config()
        self.update_nav_buttons()

    def scroll_to_section(self, section_id):
        """滚动到指定的配置部分"""
        section_map = {
            "script": self.script_section,
            "daily_routine": self.daily_routine_section,
            "wanted_quests": self.wanted_quests_section,
            "exploration": self.exploration_section,
            "realm_raid": self.realm_raid_section,
            "goryou_realm": self.goryou_realm_section,
            "shikigami_activity": self.shikigami_activity_section,
            "area_boss": self.area_boss_section
        }

        if section_id in section_map:
            section = section_map[section_id]
            # 获取滚动区域
            scroll_area = self.findChild(QScrollArea)
            if scroll_area:
                scroll_area.ensureWidgetVisible(section)


class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSA 配置编辑器")
        self.setMinimumSize(900, 700)  # 设置初始尺寸
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.config_files = [f for f in os.listdir(
            CONFIG_DIR) if f.endswith('.json') and f != 'osa.json']
        self.tab_widgets = {}
        for file in self.config_files:
            path = os.path.join(CONFIG_DIR, file)
            tab = OSAEditor(path)
            self.tabs.addTab(tab, file)
            self.tab_widgets[file] = tab
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.last_index = 0

    def on_tab_changed(self, idx):
        # 切换tab时自动保存上一个tab
        if 0 <= self.last_index < self.tabs.count():
            prev_tab = self.tabs.widget(self.last_index)
            if isinstance(prev_tab, ConfigTab):
                prev_tab.save_config()
        self.last_index = idx


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigEditor()
    window.show()
    sys.exit(app.exec())
