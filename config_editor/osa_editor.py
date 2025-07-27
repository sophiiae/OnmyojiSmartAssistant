from config_editor.log_window import LogWindow
from config_editor.script_worker import ScriptWorker
from PyQt6.QtWidgets import QTabWidget
from config_editor.widgets.select_button import SelectButton
from config_editor.widgets.value_button import ValueButton
from config_editor.main import ConfigTab
from config_editor.sections.area_boss_section import AreaBossSection
from config_editor.sections.shikigami_activity_section import ShikigamiActivitySection
from config_editor.sections.goryou_realm_section import GoryouRealmSection
from config_editor.sections.realm_raid_section import RealmRaidSection
from config_editor.sections.exploration_section import ExplorationSection
from config_editor.sections.wanted_quests_section import WantedQuestsSection
from config_editor.sections.daily_routine_section import DailyRoutineSection
from config_editor.sections.script_section import ScriptSection
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                             QWidget, QScrollArea, QCheckBox, QComboBox, QSpinBox, QLineEdit,
                             QPushButton, QHBoxLayout, QMessageBox, QLabel, QGridLayout, QGroupBox)
import sys
import os

# 获取正确的配置目录路径
def get_config_dir():
    """获取配置目录的路径"""
    if getattr(sys, 'frozen', False):
        # 如果是exe环境，使用exe所在目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 如果是开发环境，使用当前目录
        base_path = os.path.dirname(os.path.abspath(__file__))
        # 回到项目根目录
        base_path = os.path.dirname(base_path)

    config_dir = os.path.join(base_path, "configs")
    return config_dir


CONFIG_DIR = get_config_dir()

class OSAEditor(ConfigTab):
    def __init__(self, config_path):
        super().__init__(config_path)
        self.setWindowTitle("OSA 配置编辑器")
        self.script_worker = None
        self.log_window = None
        self.current_highlighted_section = None  # 当前高亮的section
        self.highlight_timer = QTimer()  # 高亮清除定时器
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.timeout.connect(self.clear_all_highlights)
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
        nav_layout.setContentsMargins(2, 2, 2, 2)  # 减少导航栏边距
        nav_layout.setSpacing(2)  # 减少导航栏间距

        # # 导航标题
        # nav_title = QLabel("快速导航:")
        # nav_layout.addWidget(nav_title)

        # 创建按钮容器，使用网格布局实现自动换行
        button_container = QWidget()
        button_layout = QGridLayout(button_container)
        button_layout.setSpacing(3)  # 减少按钮间距
        button_layout.setContentsMargins(2, 2, 2, 2)  # 减少按钮容器边距

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
                min-width: 40px;
                max-width: 50px;
                font-size: 9px;
                margin: 0px;
                padding: 2px 4px;
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

        # 为所有section添加点击事件
        self.setup_section_click_events()

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
        self.log_window = LogWindow(self.get_config_name())
        self.log_window.setParent(right_widget)
        self.log_window.set_run_button(self.run_button)  # 传递运行按钮给日志窗口
        right_layout.addWidget(self.log_window)

        # 设置右侧日志区域的固定宽度
        right_widget.setMinimumWidth(500)  # 扩大右侧宽度

        # 添加右侧日志区域到主布局
        main_layout.addWidget(right_widget)

    def setup_section_click_events(self):
        """为所有配置区域设置点击事件"""
        sections = [
            self.script_section,
            self.daily_routine_section,
            self.wanted_quests_section,
            self.exploration_section,
            self.realm_raid_section,
            self.goryou_realm_section,
            self.shikigami_activity_section,
            self.area_boss_section
        ]

        for section in sections:
            # 为每个section添加鼠标点击事件
            section.mousePressEvent = lambda event, s=section: self.on_section_clicked(
                s, event)

    def on_section_clicked(self, section, event):
        """处理配置区域的点击事件"""
        # 检查是否是右键点击
        if event.button() == Qt.MouseButton.RightButton:
            self.show_highlight_menu(section, event.globalPos())
        else:
            # 左键点击：高亮被点击的section（不会清除已高亮的区域）
            self.highlight_section(section)

        # 调用原始的mousePressEvent
        QGroupBox.mousePressEvent(section, event)

    def highlight_section(self, section):
        """高亮指定的配置区域（永久保持）"""
        # 清除之前的高亮
        if self.current_highlighted_section:
            self.clear_section_highlight(self.current_highlighted_section)

        # 设置新的高亮
        if section:
            self.set_section_highlight(section)
            self.current_highlighted_section = section
            # 不启动定时器，保持永久高亮

    def highlight_section_permanent(self, section):
        """永久高亮指定的配置区域（不自动清除）"""
        # 清除之前的高亮
        if self.current_highlighted_section:
            self.clear_section_highlight(self.current_highlighted_section)

        # 设置新的高亮
        if section:
            self.set_section_highlight(section)
            self.current_highlighted_section = section
            # 不启动定时器，保持永久高亮

    def highlight_section_temporary(self, section, duration=3000):
        """临时高亮指定的配置区域（可自定义时间）"""
        # 清除之前的高亮
        if self.current_highlighted_section:
            self.clear_section_highlight(self.current_highlighted_section)

        # 设置新的高亮
        if section:
            self.set_section_highlight(section)
            self.current_highlighted_section = section
            # 启动定时器，指定时间后自动清除高亮
            self.highlight_timer.start(duration)

    def clear_section_highlight(self, section):
        """清除配置区域的高亮"""
        if section:
            section.setStyleSheet("")

    def set_section_highlight(self, section):
        """设置配置区域的高亮边框"""
        if section:
            # 使用简洁的彩色边框高亮，去掉字体加粗
            highlight_style = """
                QGroupBox {
                    border: 2px solid #2196F3;
                    border-radius: 6px;
                    background-color: #F5F9FF;
                    margin: 1px;
                    padding: 3px;
                }
                QGroupBox::title {
                    color: #1976D2;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """
            section.setStyleSheet(highlight_style)

    def clear_all_highlights(self):
        """清除所有高亮"""
        if self.current_highlighted_section:
            self.clear_section_highlight(self.current_highlighted_section)
            self.current_highlighted_section = None
        # 停止定时器
        self.highlight_timer.stop()

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
                # 高亮选中的配置区域
                self.highlight_section(section)

    def show_highlight_menu(self, section, pos):
        """显示高亮选项菜单"""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction

        menu = QMenu(self)

        # 永久高亮选项（默认）
        permanent_action = QAction("永久高亮", self)
        permanent_action.triggered.connect(
            lambda: self.highlight_section_permanent(section))
        menu.addAction(permanent_action)

        # 临时高亮选项
        temp_action = QAction("临时高亮 (10秒)", self)
        temp_action.triggered.connect(
            lambda: self.highlight_section_temporary(section, 10000))
        menu.addAction(temp_action)

        # 清除高亮选项
        clear_action = QAction("清除高亮", self)
        clear_action.triggered.connect(self.clear_all_highlights)
        menu.addAction(clear_action)

        # 显示菜单
        menu.exec(pos)


class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSA 配置编辑器")
        self.setMinimumSize(900, 700)  # 设置初始尺寸
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 启用拖拽功能
        self.tabs.setMovable(True)

        # 连接拖拽完成信号 - 延迟连接，确保 TabBar 已初始化
        def connect_drag_signal():
            try:
                tab_bar = self.tabs.tabBar()
                if tab_bar:
                    # 直接尝试连接 tabMoved 信号
                    tab_bar.tabMoved.connect(self.on_tab_moved)
            except Exception as e:
                print(f"拖拽信号连接失败: {e}")

        # 使用 QTimer 延迟连接信号
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, connect_drag_signal)

        # 确保配置目录存在
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)

        # 获取配置文件列表
        try:
            self.config_files = [f for f in os.listdir(
                CONFIG_DIR) if f.endswith('.json') and f != 'custom_order.json']
        except FileNotFoundError:
            self.config_files = []
            print(f"警告：配置目录 {CONFIG_DIR} 不存在或无法访问")

        # 保存当前的自定义顺序
        self.custom_order = []

        # 排序方式：只使用自定义排序
        self.sort_mode = 'custom'

        # 加载保存的自定义顺序
        self.load_custom_order()

        self.tab_widgets = {}

        # 获取排序后的配置文件列表
        config_files_ordered = self.get_sorted_config_files()

        for file in config_files_ordered:
            path = os.path.join(CONFIG_DIR, file)
            try:
                tab = OSAEditor(path)
                self.tabs.addTab(tab, file)
                self.tab_widgets[file] = tab
            except Exception as e:
                print(f"警告：无法加载配置文件 {file}: {e}")

        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.last_index = 0

        # 设置右键菜单
        self.setup_context_menu()

        # 如果没有找到任何配置文件，显示提示
        if not self.config_files:
            from PyQt6.QtWidgets import QLabel
            no_config_label = QLabel("未找到配置文件。\n请确保configs目录中有.json配置文件。")
            no_config_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_config_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #666;
                    padding: 20px;
                }
            """)
            self.tabs.addTab(no_config_label, "无配置")

    def get_sorted_config_files(self):
        """获取排序后的配置文件列表（使用自定义顺序）"""
        config_files_ordered = []

        # 排除osa.json，不显示在UI中
        other_files = [f for f in self.config_files if f != 'osa.json']

        # 使用用户自定义顺序
        if hasattr(self, 'custom_order') and self.custom_order:
            # 按照保存的自定义顺序排列
            for file in self.custom_order:
                if file in other_files:
                    config_files_ordered.append(file)
                    other_files.remove(file)

            # 添加剩余的文件（按时间排序）
            if other_files:
                file_times = []
                for file in other_files:
                    file_path = os.path.join(CONFIG_DIR, file)
                    try:
                        creation_time = os.path.getctime(file_path)
                        file_times.append((file, creation_time))
                    except OSError:
                        try:
                            creation_time = os.path.getmtime(file_path)
                            file_times.append((file, creation_time))
                        except OSError:
                            file_times.append((file, 0))

                file_times.sort(key=lambda x: x[1], reverse=True)
                config_files_ordered.extend([file for file, _ in file_times])
        else:
            # 如果没有自定义顺序，使用时间排序
            file_times = []
            for file in other_files:
                file_path = os.path.join(CONFIG_DIR, file)
                try:
                    creation_time = os.path.getctime(file_path)
                    file_times.append((file, creation_time))
                except OSError:
                    try:
                        creation_time = os.path.getmtime(file_path)
                        file_times.append((file, creation_time))
                    except OSError:
                        file_times.append((file, 0))

            file_times.sort(key=lambda x: x[1], reverse=True)
            config_files_ordered.extend([file for file, _ in file_times])

        return config_files_ordered

    def change_sort_mode(self, mode):
        """改变排序模式并重新加载tabs（已简化，只支持自定义排序）"""
        self.sort_mode = 'custom'
        self.reload_tabs()

    def reload_tabs(self):
        """重新加载所有tabs"""
        # 保存当前选中的tab索引
        current_index = self.tabs.currentIndex()

        # 清空所有tabs
        self.tabs.clear()

        # 重新加载配置文件
        config_files_ordered = self.get_sorted_config_files()

        for file in config_files_ordered:
            path = os.path.join(CONFIG_DIR, file)
            try:
                tab = OSAEditor(path)
                self.tabs.addTab(tab, file)
                self.tab_widgets[file] = tab
            except Exception as e:
                print(f"警告：无法加载配置文件 {file}: {e}")

        # 恢复选中的tab
        if 0 <= current_index < self.tabs.count():
            self.tabs.setCurrentIndex(current_index)

    def setup_context_menu(self):
        """设置右键菜单"""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtCore import Qt

        # 设置tabs的右键菜单
        self.tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """显示右键菜单"""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction

        menu = QMenu(self)

        # 刷新配置
        refresh_action = QAction("刷新配置文件", self)
        refresh_action.triggered.connect(self.reload_tabs)
        menu.addAction(refresh_action)

        # 显示菜单
        menu.exec(self.tabs.mapToGlobal(position))

    def on_tab_moved(self, from_index, to_index):
        """当标签页被拖拽移动时调用"""
        # 更新自定义顺序
        self.update_custom_order()

    def load_custom_order(self):
        """从文件加载自定义顺序"""
        import json

        order_file = os.path.join(CONFIG_DIR, "custom_order.json")
        try:
            if os.path.exists(order_file):
                with open(order_file, 'r', encoding='utf-8') as f:
                    self.custom_order = json.load(f)
                    print(f"已加载自定义顺序: {self.custom_order}")
            else:
                self.custom_order = []
        except Exception as e:
            print(f"加载自定义顺序失败: {e}")
            self.custom_order = []

    def save_custom_order(self):
        """保存自定义顺序到文件"""
        import json

        order_file = os.path.join(CONFIG_DIR, "custom_order.json")
        try:
            with open(order_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_order, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义顺序失败: {e}")

    def update_custom_order(self):
        """更新自定义顺序"""
        self.custom_order = []
        for i in range(self.tabs.count()):
            tab_text = self.tabs.tabText(i)
            if tab_text != "无配置":  # 排除提示标签
                self.custom_order.append(tab_text)

        # 保存自定义顺序
        self.save_custom_order()

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
