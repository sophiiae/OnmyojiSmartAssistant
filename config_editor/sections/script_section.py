from PyQt6.QtWidgets import (QCheckBox, QComboBox, QGroupBox, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QLabel)
from config_editor.widgets.value_button import ValueButton
from config_editor.widgets.select_button import SelectButton

def add_labeled_widget(layout, label_text, widget):
    row = QHBoxLayout()
    row.addWidget(QLabel(label_text))
    row.addWidget(widget)
    layout.addLayout(row)

class ScriptSection(QGroupBox):
    def __init__(self, config):
        super().__init__("脚本设置")
        self.config = config
        layout = QVBoxLayout(self)
        # 设备设置
        device = config["script"]["device"]
        self.serial_edit = QLineEdit(str(device.get("serial", "")))
        add_labeled_widget(layout, "设备序列号", self.serial_edit)
        self.handle_edit = QLineEdit(str(device.get("handle", "")))
        add_labeled_widget(layout, "句柄", self.handle_edit)
        # self.screenshot_combo = QComboBox()
        # self.screenshot_combo.addItems(["ADB_nc", "ADB", "minicap"])
        # self.screenshot_combo.setCurrentText(
        #     device.get("screenshot_method", "ADB_nc"))
        # add_labeled_widget(layout, "截图方法", self.screenshot_combo)
        # self.control_combo = QComboBox()
        # self.control_combo.addItems(["minitouch", "ADB"])
        # self.control_combo.setCurrentText(
        #     device.get("control_method", "minitouch"))
        # add_labeled_widget(layout, "控制方法", self.control_combo)
        # 优化设置
        opt = config["script"]["optimization"]
        self.screenshot_interval_spin = ValueButton()
        self.screenshot_interval_spin.setRange(1, 50)  # 0.1-5.0 转换为 1-50
        self.screenshot_interval_spin.setValue(
            int(opt.get("screenshot_interval", 0.3) * 10))
        add_labeled_widget(layout, "截图间隔(秒)", self.screenshot_interval_spin)
        self.combat_interval_spin = ValueButton()
        self.combat_interval_spin.setRange(1, 50)  # 0.1-5.0 转换为 1-50
        self.combat_interval_spin.setValue(
            int(opt.get("combat_screenshot_interval", 1.0) * 10))
        add_labeled_widget(layout, "战斗截图间隔(秒)", self.combat_interval_spin)
        self.schedule_rule_edit = QLineEdit(
            str(opt.get("schedule_rule", "FIFO")))
        add_labeled_widget(layout, "调度规则", self.schedule_rule_edit)
        # 错误处理
        err = config["script"]["error_handler"]
        self.when_network_abnormal_edit = QLineEdit(
            str(err.get("when_network_abnormal", "")))
        add_labeled_widget(layout, "网络异常时", self.when_network_abnormal_edit)
        self.when_network_error_edit = QLineEdit(
            str(err.get("when_network_error", "")))
        add_labeled_widget(layout, "网络错误时", self.when_network_error_edit)
        self.cache_clear_request_check = QCheckBox("请求清理缓存")
        self.cache_clear_request_check.setChecked(
            err.get("cache_clear_request", False))
        layout.addWidget(self.cache_clear_request_check)

    def update_config(self):
        self.config["script"]["device"]["serial"] = self.serial_edit.text()
        self.config["script"]["device"]["handle"] = self.handle_edit.text()
        # self.config["script"]["device"]["screenshot_method"] = self.screenshot_combo.currentText()
        # self.config["script"]["device"]["control_method"] = self.control_combo.currentText()
        self.config["script"]["optimization"]["screenshot_interval"] = self.screenshot_interval_spin.value() / 10
        self.config["script"]["optimization"]["combat_screenshot_interval"] = self.combat_interval_spin.value() / 10
        self.config["script"]["optimization"]["schedule_rule"] = self.schedule_rule_edit.text()
        self.config["script"]["error_handler"]["when_network_abnormal"] = self.when_network_abnormal_edit.text()
        self.config["script"]["error_handler"]["when_network_error"] = self.when_network_error_edit.text()
        self.config["script"]["error_handler"]["cache_clear_request"] = self.cache_clear_request_check.isChecked()
