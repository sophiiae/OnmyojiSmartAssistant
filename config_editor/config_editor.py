from PyQt6.QtWidgets import QMainWindow, QTabWidget, QApplication, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu
import sys
import os
import json
from module.base.logger import logger
from config_editor.osa_editor import OSAEditor, CONFIG_DIR

class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Onmyoji Smart Assistant")
        self.setMinimumSize(900, 700)  # 设置初始尺寸

        # 设置主窗口背景色和全局样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F2ECF9;  /* 淡紫色背景 */
            }
            
            /* 全局checkbox样式 */
            QCheckBox::indicator:unchecked {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 4px;
                width: 14px;
                height: 14px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #aa66cc;
                border: 1px solid #aa66cc;
                border-radius: 4px;
                width: 14px;
                height: 14px;
            }
            
            QCheckBox::indicator:unchecked:hover {
                border: 1px solid #aa66cc;
                background-color: white;
            }
            
            QCheckBox::indicator:checked:hover {
                background-color: #9b72cf;
                border: 1px solid #9b72cf;
            }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # 设置标签页样式，使当前选中的标签页更突出
        self.setup_tab_styles()

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
                logger.warning(f"拖拽信号连接失败: {e}")

        # 使用 QTimer 延迟连接信号
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
            logger.warning(f"配置目录 {CONFIG_DIR} 不存在或无法访问")

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
                # 显示时去掉.json后缀
                display_name = file.replace('.json', '')
                self.tabs.addTab(tab, display_name)
                self.tab_widgets[file] = tab
            except Exception as e:
                logger.warning(f"无法加载配置文件 {file}: {e}")

        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.last_index = 0

        # 设置右键菜单
        self.setup_context_menu()

        # 如果没有找到任何配置文件，显示提示
        if not self.config_files:
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

    def setup_tab_styles(self):
        """设置标签页样式，使当前选中的标签页更突出"""
        tab_style = """
            QTabWidget::pane {
                border: 2px solid #532b88;
                background: #fbfaff;  /* 更改为浅紫色背景 */
            }
            
            QTabBar::tab {
                background: #f2ebfb;  /* 更改为浅紫色背景 */
                color: #333333;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #f2ebfb;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: normal;
                min-width: 40px;
            }

            QTabBar::tab:unselected {
                background: #ebd9fc;  /* 更改为稍深的紫色 */
                color: #000000;
            }
            
            QTabBar::tab:hover {
                background: #C3A3F5;  /* 更改为稍深的紫色 */
                color: #000000;
            }
            
            QTabBar::tab:selected {
                background: #532b88;
                color: white;
                font-weight: bold;
                border: 1px solid #532b88;
            }
            
        """
        self.tabs.setStyleSheet(tab_style)

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
                # 显示时去掉.json后缀
                display_name = file.replace('.json', '')
                self.tabs.addTab(tab, display_name)
                self.tab_widgets[file] = tab
            except Exception as e:
                logger.warning(f"无法加载配置文件 {file}: {e}")

        # 恢复选中的tab
        if 0 <= current_index < self.tabs.count():
            self.tabs.setCurrentIndex(current_index)

    def setup_context_menu(self):
        """设置右键菜单"""
        # 设置tabs的右键菜单
        self.tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """显示右键菜单"""
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
        order_file = os.path.join(CONFIG_DIR, "custom_order.json")
        try:
            if os.path.exists(order_file):
                with open(order_file, 'r', encoding='utf-8') as f:
                    self.custom_order = json.load(f)
                    pass  # 已加载自定义顺序，但不输出到控制台
            else:
                self.custom_order = []
        except Exception as e:
            logger.warning(f"加载自定义顺序失败: {e}")
            self.custom_order = []

    def save_custom_order(self):
        """保存自定义顺序到文件"""
        order_file = os.path.join(CONFIG_DIR, "custom_order.json")
        try:
            with open(order_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_order, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存自定义顺序失败: {e}")

    def update_custom_order(self):
        """更新自定义顺序"""
        self.custom_order = []
        for i in range(self.tabs.count()):
            tab_text = self.tabs.tabText(i)
            if tab_text != "无配置":  # 排除提示标签
                # 添加.json后缀以匹配实际文件名
                self.custom_order.append(tab_text + '.json')

        # 保存自定义顺序
        self.save_custom_order()

    def on_tab_changed(self, idx):
        # 切换tab时自动保存上一个tab
        if 0 <= self.last_index < self.tabs.count():
            prev_tab = self.tabs.widget(self.last_index)
            if prev_tab:
                try:
                    save_method = getattr(prev_tab, 'save_config', None)
                    if save_method and callable(save_method):
                        save_method()
                except Exception:
                    pass  # 忽略保存错误

        # 只激活当前tab的日志窗口，避免日志串到其他窗口
        current_tab = self.tabs.widget(idx)
        if current_tab:
            try:
                log_window = getattr(current_tab, 'log_window', None)
                if log_window:
                    # 只激活当前tab的日志窗口
                    log_window.set_active(True)
            except Exception:
                pass  # 忽略日志窗口操作错误

        self.last_index = idx
