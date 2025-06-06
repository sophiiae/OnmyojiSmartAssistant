import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QCheckBox,
                             QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
                             QScrollArea, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt

class ConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OSA 配置编辑器")
        self.setMinimumSize(800, 600)

        # 加载配置文件
        try:
            with open('configs/osa.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法加载配置文件: {str(e)}")
            sys.exit(1)

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # 创建设置界面
        self.create_script_settings(scroll_layout)
        self.create_daily_routine_settings(scroll_layout)
        self.create_wanted_quests_settings(scroll_layout)
        self.create_exploration_settings(scroll_layout)
        self.create_realm_raid_settings(scroll_layout)
        self.create_goryou_realm_settings(scroll_layout)
        self.create_shikigami_activity_settings(scroll_layout)

        # 添加保存按钮
        save_button = QPushButton("保存配置")
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)

    def create_script_settings(self, layout):
        group = QGroupBox("脚本设置")
        group_layout = QVBoxLayout()

        # Device settings
        device_group = QGroupBox("设备设置")
        device_layout = QVBoxLayout()

        serial_layout = QHBoxLayout()
        serial_layout.addWidget(QLabel("设备序列号:"))
        self.serial_edit = QLineEdit(self.config["script"]["device"]["serial"])
        serial_layout.addWidget(self.serial_edit)
        device_layout.addLayout(serial_layout)

        screenshot_layout = QHBoxLayout()
        screenshot_layout.addWidget(QLabel("截图方法:"))
        self.screenshot_combo = QComboBox()
        self.screenshot_combo.addItems(["ADB_nc", "ADB", "minicap"])
        self.screenshot_combo.setCurrentText(
            self.config["script"]["device"]["screenshot_method"])
        screenshot_layout.addWidget(self.screenshot_combo)
        device_layout.addLayout(screenshot_layout)

        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("控制方法:"))
        self.control_combo = QComboBox()
        self.control_combo.addItems(["minitouch", "ADB"])
        self.control_combo.setCurrentText(
            self.config["script"]["device"]["control_method"])
        control_layout.addWidget(self.control_combo)
        device_layout.addLayout(control_layout)

        device_group.setLayout(device_layout)
        group_layout.addWidget(device_group)

        # Optimization settings
        opt_group = QGroupBox("优化设置")
        opt_layout = QVBoxLayout()

        screenshot_interval_layout = QHBoxLayout()
        screenshot_interval_layout.addWidget(QLabel("截图间隔:"))
        self.screenshot_interval_spin = QDoubleSpinBox()
        self.screenshot_interval_spin.setRange(0.1, 5.0)
        self.screenshot_interval_spin.setSingleStep(0.1)
        self.screenshot_interval_spin.setValue(
            self.config["script"]["optimization"]["screenshot_interval"])
        screenshot_interval_layout.addWidget(self.screenshot_interval_spin)
        opt_layout.addLayout(screenshot_interval_layout)

        combat_interval_layout = QHBoxLayout()
        combat_interval_layout.addWidget(QLabel("战斗截图间隔:"))
        self.combat_interval_spin = QDoubleSpinBox()
        self.combat_interval_spin.setRange(0.1, 5.0)
        self.combat_interval_spin.setSingleStep(0.1)
        self.combat_interval_spin.setValue(
            self.config["script"]["optimization"]["combat_screenshot_interval"])
        combat_interval_layout.addWidget(self.combat_interval_spin)
        opt_layout.addLayout(combat_interval_layout)

        opt_group.setLayout(opt_layout)
        group_layout.addWidget(opt_group)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_daily_routine_settings(self, layout):
        group = QGroupBox("日常任务设置")
        group_layout = QVBoxLayout()

        # Harvest settings
        harvest_group = QGroupBox("收获设置")
        harvest_layout = QVBoxLayout()

        self.enable_jade = QCheckBox("启用勾玉")
        self.enable_jade.setChecked(
            self.config["daily_routine"]["harvest_config"]["enable_jade"])
        harvest_layout.addWidget(self.enable_jade)

        self.enable_sign = QCheckBox("启用签到")
        self.enable_sign.setChecked(
            self.config["daily_routine"]["harvest_config"]["enable_sign"])
        harvest_layout.addWidget(self.enable_sign)

        self.enable_sign_999 = QCheckBox("启用999签到")
        self.enable_sign_999.setChecked(
            self.config["daily_routine"]["harvest_config"]["enable_sign_999"])
        harvest_layout.addWidget(self.enable_sign_999)

        self.enable_mail = QCheckBox("启用邮件")
        self.enable_mail.setChecked(
            self.config["daily_routine"]["harvest_config"]["enable_mail"])
        harvest_layout.addWidget(self.enable_mail)

        self.enable_soul = QCheckBox("启用御魂")
        self.enable_soul.setChecked(
            self.config["daily_routine"]["harvest_config"]["enable_soul"])
        harvest_layout.addWidget(self.enable_soul)

        self.enable_ap = QCheckBox("启用体力")
        self.enable_ap.setChecked(
            self.config["daily_routine"]["harvest_config"]["enable_ap"])
        harvest_layout.addWidget(self.enable_ap)

        harvest_group.setLayout(harvest_layout)
        group_layout.addWidget(harvest_group)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_wanted_quests_settings(self, layout):
        group = QGroupBox("悬赏任务设置")
        group_layout = QVBoxLayout()

        accept_layout = QHBoxLayout()
        accept_layout.addWidget(QLabel("接受任务类型:"))
        self.accept_type_combo = QComboBox()
        self.accept_type_combo.addItems(["勾玉", "金币", "体力", "御魂"])
        self.accept_type_combo.setCurrentText(
            self.config["wanted_quests"]["accept_quest_config"]["accept_type"])
        accept_layout.addWidget(self.accept_type_combo)
        group_layout.addLayout(accept_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_exploration_settings(self, layout):
        group = QGroupBox("探索设置")
        group_layout = QVBoxLayout()

        # Exploration config
        config_group = QGroupBox("探索配置")
        config_layout = QVBoxLayout()

        self.buff_gold_50 = QCheckBox("50%金币加成")
        self.buff_gold_50.setChecked(
            self.config["exploration"]["exploration_config"]["buff_gold_50"])
        config_layout.addWidget(self.buff_gold_50)

        self.buff_gold_100 = QCheckBox("100%金币加成")
        self.buff_gold_100.setChecked(
            self.config["exploration"]["exploration_config"]["buff_gold_100"])
        config_layout.addWidget(self.buff_gold_100)

        self.buff_exp_50 = QCheckBox("50%经验加成")
        self.buff_exp_50.setChecked(
            self.config["exploration"]["exploration_config"]["buff_exp_50"])
        config_layout.addWidget(self.buff_exp_50)

        self.buff_exp_100 = QCheckBox("100%经验加成")
        self.buff_exp_100.setChecked(
            self.config["exploration"]["exploration_config"]["buff_exp_100"])
        config_layout.addWidget(self.buff_exp_100)

        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("最大次数:"))
        self.count_max_spin = QSpinBox()
        self.count_max_spin.setRange(1, 100)
        self.count_max_spin.setValue(
            self.config["exploration"]["exploration_config"]["count_max"])
        count_layout.addWidget(self.count_max_spin)
        config_layout.addLayout(count_layout)

        chapter_layout = QHBoxLayout()
        chapter_layout.addWidget(QLabel("章节:"))
        self.chapter_combo = QComboBox()
        self.chapter_combo.addItems([f"第{i}章" for i in range(1, 29)])
        self.chapter_combo.setCurrentText(
            self.config["exploration"]["exploration_config"]["chapter"])
        chapter_layout.addWidget(self.chapter_combo)
        config_layout.addLayout(chapter_layout)

        config_group.setLayout(config_layout)
        group_layout.addWidget(config_group)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_realm_raid_settings(self, layout):
        group = QGroupBox("结界突破设置")
        group_layout = QVBoxLayout()

        # Raid config
        config_group = QGroupBox("突破配置")
        config_layout = QVBoxLayout()

        tickets_layout = QHBoxLayout()
        tickets_layout.addWidget(QLabel("所需门票:"))
        self.tickets_spin = QSpinBox()
        self.tickets_spin.setRange(1, 100)
        self.tickets_spin.setValue(
            self.config["realm_raid"]["raid_config"]["tickets_required"])
        tickets_layout.addWidget(self.tickets_spin)
        config_layout.addLayout(tickets_layout)

        self.exit_two = QCheckBox("退出两次")
        self.exit_two.setChecked(
            self.config["realm_raid"]["raid_config"]["exit_two"])
        config_layout.addWidget(self.exit_two)

        order_layout = QHBoxLayout()
        order_layout.addWidget(QLabel("攻击顺序:"))
        self.order_edit = QLineEdit(
            self.config["realm_raid"]["raid_config"]["order_attack"])
        order_layout.addWidget(self.order_edit)
        config_layout.addLayout(order_layout)

        self.three_refresh = QCheckBox("三次刷新")
        self.three_refresh.setChecked(
            self.config["realm_raid"]["raid_config"]["three_refresh"])
        config_layout.addWidget(self.three_refresh)

        fail_layout = QHBoxLayout()
        fail_layout.addWidget(QLabel("攻击失败时:"))
        self.fail_combo = QComboBox()
        self.fail_combo.addItems(["Continue", "Stop", "Retry"])
        self.fail_combo.setCurrentText(
            self.config["realm_raid"]["raid_config"]["when_attack_fail"])
        fail_layout.addWidget(self.fail_combo)
        config_layout.addLayout(fail_layout)

        config_group.setLayout(config_layout)
        group_layout.addWidget(config_group)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_goryou_realm_settings(self, layout):
        group = QGroupBox("御灵设置")
        group_layout = QVBoxLayout()

        # Goryou config
        config_group = QGroupBox("御灵配置")
        config_layout = QVBoxLayout()

        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("御灵类型:"))
        self.goryou_class_combo = QComboBox()
        self.goryou_class_combo.addItems(["暗孔雀", "白藏主", "黑豹", "神龙"])
        self.goryou_class_combo.setCurrentText(
            self.config["goryou_realm"]["goryou_config"]["goryou_class"])
        class_layout.addWidget(self.goryou_class_combo)
        config_layout.addLayout(class_layout)

        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("最大次数:"))
        self.goryou_count_spin = QSpinBox()
        self.goryou_count_spin.setRange(1, 100)
        self.goryou_count_spin.setValue(
            self.config["goryou_realm"]["goryou_config"]["count_max"])
        count_layout.addWidget(self.goryou_count_spin)
        config_layout.addLayout(count_layout)

        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("层数:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["一层", "二层", "三层"])
        self.level_combo.setCurrentText(
            self.config["goryou_realm"]["goryou_config"]["level"])
        level_layout.addWidget(self.level_combo)
        config_layout.addLayout(level_layout)

        config_group.setLayout(config_layout)
        group_layout.addWidget(config_group)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def create_shikigami_activity_settings(self, layout):
        group = QGroupBox("式神活动设置")
        group_layout = QVBoxLayout()

        # Climb config
        config_group = QGroupBox("爬塔配置")
        config_layout = QVBoxLayout()

        self.enable_ap_mode = QCheckBox("启用体力模式")
        self.enable_ap_mode.setChecked(
            self.config["shikigami_activity"]["climb_config"]["enable_ap_mode"])
        config_layout.addWidget(self.enable_ap_mode)

        self.auto_switch = QCheckBox("自动切换")
        self.auto_switch.setChecked(
            self.config["shikigami_activity"]["climb_config"]["auto_switch"])
        config_layout.addWidget(self.auto_switch)

        ticket_layout = QHBoxLayout()
        ticket_layout.addWidget(QLabel("最大门票:"))
        self.ticket_max_spin = QSpinBox()
        self.ticket_max_spin.setRange(1, 100)
        self.ticket_max_spin.setValue(
            self.config["shikigami_activity"]["climb_config"]["ticket_max"])
        ticket_layout.addWidget(self.ticket_max_spin)
        config_layout.addLayout(ticket_layout)

        ap_layout = QHBoxLayout()
        ap_layout.addWidget(QLabel("最大体力:"))
        self.ap_max_spin = QSpinBox()
        self.ap_max_spin.setRange(1, 1000)
        self.ap_max_spin.setValue(
            self.config["shikigami_activity"]["climb_config"]["ap_max"])
        ap_layout.addWidget(self.ap_max_spin)
        config_layout.addLayout(ap_layout)

        config_group.setLayout(config_layout)
        group_layout.addWidget(config_group)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def save_config(self):
        try:
            # 更新配置
            self.config["script"]["device"]["serial"] = self.serial_edit.text()
            self.config["script"]["device"]["screenshot_method"] = self.screenshot_combo.currentText()
            self.config["script"]["device"]["control_method"] = self.control_combo.currentText()

            self.config["script"]["optimization"]["screenshot_interval"] = self.screenshot_interval_spin.value()
            self.config["script"]["optimization"]["combat_screenshot_interval"] = self.combat_interval_spin.value()

            self.config["daily_routine"]["harvest_config"]["enable_jade"] = self.enable_jade.isChecked()
            self.config["daily_routine"]["harvest_config"]["enable_sign"] = self.enable_sign.isChecked()
            self.config["daily_routine"]["harvest_config"]["enable_sign_999"] = self.enable_sign_999.isChecked()
            self.config["daily_routine"]["harvest_config"]["enable_mail"] = self.enable_mail.isChecked()
            self.config["daily_routine"]["harvest_config"]["enable_soul"] = self.enable_soul.isChecked()
            self.config["daily_routine"]["harvest_config"]["enable_ap"] = self.enable_ap.isChecked()

            self.config["wanted_quests"]["accept_quest_config"]["accept_type"] = self.accept_type_combo.currentText()

            self.config["exploration"]["exploration_config"]["buff_gold_50"] = self.buff_gold_50.isChecked()
            self.config["exploration"]["exploration_config"]["buff_gold_100"] = self.buff_gold_100.isChecked()
            self.config["exploration"]["exploration_config"]["buff_exp_50"] = self.buff_exp_50.isChecked()
            self.config["exploration"]["exploration_config"]["buff_exp_100"] = self.buff_exp_100.isChecked()
            self.config["exploration"]["exploration_config"]["count_max"] = self.count_max_spin.value()
            self.config["exploration"]["exploration_config"]["chapter"] = self.chapter_combo.currentText()

            self.config["realm_raid"]["raid_config"]["tickets_required"] = self.tickets_spin.value()
            self.config["realm_raid"]["raid_config"]["exit_two"] = self.exit_two.isChecked(
            )
            self.config["realm_raid"]["raid_config"]["order_attack"] = self.order_edit.text(
            )
            self.config["realm_raid"]["raid_config"]["three_refresh"] = self.three_refresh.isChecked()
            self.config["realm_raid"]["raid_config"]["when_attack_fail"] = self.fail_combo.currentText()

            self.config["goryou_realm"]["goryou_config"]["goryou_class"] = self.goryou_class_combo.currentText()
            self.config["goryou_realm"]["goryou_config"]["count_max"] = self.goryou_count_spin.value()
            self.config["goryou_realm"]["goryou_config"]["level"] = self.level_combo.currentText()

            self.config["shikigami_activity"]["climb_config"]["enable_ap_mode"] = self.enable_ap_mode.isChecked()
            self.config["shikigami_activity"]["climb_config"]["auto_switch"] = self.auto_switch.isChecked()
            self.config["shikigami_activity"]["climb_config"]["ticket_max"] = self.ticket_max_spin.value()
            self.config["shikigami_activity"]["climb_config"]["ap_max"] = self.ap_max_spin.value()

            # 保存到文件
            with open('osa.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            QMessageBox.information(self, "成功", "配置已保存！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置时出错: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigEditor()
    window.show()
    sys.exit(app.exec())
