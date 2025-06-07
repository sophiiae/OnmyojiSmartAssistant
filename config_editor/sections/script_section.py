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
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        script_config = self.config["script"]

        # 设备设置
        device = script_config["device"]
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
        opt = script_config["optimization"]
        # 截图间隔和战斗截图间隔同一行
        row = QHBoxLayout()
        self.screenshot_interval = ValueButton()
        self.screenshot_interval.setRange(1, 50)
        self.screenshot_interval.setValue(
            int(float(opt.get("screenshot_interval", 1)) * 10))
        row.addWidget(QLabel("截图间隔"))
        row.addWidget(self.screenshot_interval)
        row.addSpacing(20)
        self.combat_screenshot_interval = ValueButton()
        self.combat_screenshot_interval.setRange(1, 50)
        self.combat_screenshot_interval.setValue(
            int(float(opt.get("combat_screenshot_interval", 1)) * 10))
        row.addWidget(QLabel("战斗截图间隔"))
        row.addWidget(self.combat_screenshot_interval)
        layout.addLayout(row)
        self.schedule_rule_edit = QLineEdit(
            str(opt.get("schedule_rule", "FIFO")))
        add_labeled_widget(layout, "调度规则", self.schedule_rule_edit)
        # 错误处理
        err = script_config["error_handler"]
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
        script_config = self.config["script"]
        script_config["device"]["serial"] = self.serial_edit.text()
        script_config["device"]["handle"] = self.handle_edit.text()
        # script_config["device"]["screenshot_method"] = self.screenshot_combo.currentText()
        # script_config["device"]["control_method"] = self.control_combo.currentText()
        script_config["optimization"]["screenshot_interval"] = self.screenshot_interval.value(
        ) / 10
        script_config["optimization"]["combat_screenshot_interval"] = self.combat_screenshot_interval.value() / 10
        script_config["optimization"]["schedule_rule"] = self.schedule_rule_edit.text()
        script_config["error_handler"]["when_network_abnormal"] = self.when_network_abnormal_edit.text()
        script_config["error_handler"]["when_network_error"] = self.when_network_error_edit.text()
        script_config["error_handler"]["cache_clear_request"] = self.cache_clear_request_check.isChecked()
