import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                             QWidget, QScrollArea, QPushButton, QMessageBox, QTabWidget, QCheckBox, QComboBox, QSpinBox, QLineEdit)
from config_editor.sections.script_section import ScriptSection
from config_editor.sections.daily_routine_section import DailyRoutineSection
from config_editor.sections.wanted_quests_section import WantedQuestsSection
from config_editor.sections.exploration_section import ExplorationSection
from config_editor.sections.realm_raid_section import RealmRaidSection
from config_editor.sections.goryou_realm_section import GoryouRealmSection
from config_editor.sections.shikigami_activity_section import ShikigamiActivitySection
from config_editor.sections.area_boss_section import AreaBossSection

CONFIG_DIR = "configs"

class ConfigTab(QWidget):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
        self.load_config()
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        # 分组
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
        # 自动保存
        self.install_auto_save()

    def load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def save_config(self):
        self.script_section.update_config()
        self.daily_routine_section.update_config()
        self.wanted_quests_section.update_config()
        self.exploration_section.update_config()
        self.realm_raid_section.update_config()
        self.goryou_realm_section.update_config()
        self.shikigami_activity_section.update_config()
        self.area_boss_section.update_config()
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def install_auto_save(self):
        # 给所有控件加信号，内容变动时自动保存
        for section in [self.script_section, self.daily_routine_section, self.wanted_quests_section,
                        self.exploration_section, self.realm_raid_section, self.goryou_realm_section,
                        self.shikigami_activity_section, self.area_boss_section]:
            for child in section.findChildren((QCheckBox, QComboBox, QSpinBox, QLineEdit)):
                if hasattr(child, 'textChanged'):
                    child.textChanged.connect(self.save_config)
                if hasattr(child, 'currentIndexChanged'):
                    child.currentIndexChanged.connect(self.save_config)
                if hasattr(child, 'stateChanged'):
                    child.stateChanged.connect(self.save_config)
                if hasattr(child, 'valueChanged'):
                    child.valueChanged.connect(self.save_config)

class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSA 配置编辑器")
        self.setMinimumSize(900, 700)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.config_files = [f for f in os.listdir(
            CONFIG_DIR) if f.endswith('.json')]
        self.tab_widgets = {}
        for file in self.config_files:
            path = os.path.join(CONFIG_DIR, file)
            tab = ConfigTab(path)
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
