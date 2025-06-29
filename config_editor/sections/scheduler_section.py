from PyQt6.QtWidgets import (QCheckBox, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QLabel, QTimeEdit, QSizePolicy, QRadioButton)
from PyQt6.QtCore import QTime
from config_editor.widgets.select_button import SelectButton
from config_editor.utils import add_left_row
import re

def parse_datetime(dt_str):
    # 解析 yyyy-MM-dd HH:mm:ss
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})", dt_str)
    if m:
        return [int(x) for x in m.groups()]
    return [2023, 1, 1, 0, 0, 0]

def format_datetime(year, month, day, hour, minute, second):
    return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

def parse_interval(interval_str):
    m = re.match(r"(\d{2}):(\d{2}):(\d{2}):(\d{2})", interval_str)
    if m:
        return [int(x) for x in m.groups()]
    return [0, 0, 0, 0]

def format_interval(day, hour, minute, second):
    return f"{day:02d}:{hour:02d}:{minute:02d}:{second:02d}"

class DateTimeSelectRow:
    def __init__(self, label, default_str):
        self.label = label
        y, m, d, h, mi, s = parse_datetime(default_str)
        self.year = SelectButton()
        self.year.addItems([str(i) for i in range(2023, 2031)])
        self.year.setCurrentText(str(y))
        self.year.setFixedWidth(44)
        self.year.setSizePolicy(QSizePolicy.Policy.Fixed,
                                QSizePolicy.Policy.Fixed)
        self.month = SelectButton()
        self.month.addItems([f"{i:02d}" for i in range(1, 13)])
        self.month.setCurrentText(f"{m:02d}")
        self.month.setFixedWidth(28)
        self.month.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.day = SelectButton()
        self.day.addItems([f"{i:02d}" for i in range(1, 32)])
        self.day.setCurrentText(f"{d:02d}")
        self.day.setFixedWidth(28)
        self.day.setSizePolicy(QSizePolicy.Policy.Fixed,
                               QSizePolicy.Policy.Fixed)
        self.hour = SelectButton()
        self.hour.addItems([f"{i:02d}" for i in range(0, 24)])
        self.hour.setCurrentText(f"{h:02d}")
        self.hour.setFixedWidth(28)
        self.hour.setSizePolicy(QSizePolicy.Policy.Fixed,
                                QSizePolicy.Policy.Fixed)
        self.minute = SelectButton()
        self.minute.addItems([f"{i:02d}" for i in range(0, 60)])
        self.minute.setCurrentText(f"{mi:02d}")
        self.minute.setFixedWidth(28)
        self.minute.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.second = SelectButton()
        self.second.addItems([f"{i:02d}" for i in range(0, 60)])
        self.second.setCurrentText(f"{s:02d}")
        self.second.setFixedWidth(28)
        self.second.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def get(self):
        return format_datetime(int(self.year.currentText()), int(self.month.currentText()), int(self.day.currentText()),
                               int(self.hour.currentText()), int(self.minute.currentText()), int(self.second.currentText()))

    def widgets(self):
        return [QLabel(self.label),
                'STRETCH',
                self.year, QLabel(
                    "-"), self.month, QLabel("-"), self.day, QLabel(" "),
                self.hour, QLabel(":"), self.minute, QLabel(":"), self.second]

    def update_gui(self, value):
        """更新GUI显示"""
        y, m, d, h, mi, s = parse_datetime(value)
        self.year.setCurrentText(str(y))
        self.month.setCurrentText(f"{m:02d}")
        self.day.setCurrentText(f"{d:02d}")
        self.hour.setCurrentText(f"{h:02d}")
        self.minute.setCurrentText(f"{mi:02d}")
        self.second.setCurrentText(f"{s:02d}")

class IntervalSelectRow:
    def __init__(self, label, default_str):
        self.label = label
        d, h, mi, s = parse_interval(default_str)
        self.day = SelectButton()
        self.day.addItems([f"{i:02d}" for i in range(0, 31)])
        self.day.setCurrentText(f"{d:02d}")
        self.day.setFixedWidth(28)
        self.day.setSizePolicy(QSizePolicy.Policy.Fixed,
                               QSizePolicy.Policy.Fixed)
        self.hour = SelectButton()
        self.hour.addItems([f"{i:02d}" for i in range(0, 24)])
        self.hour.setCurrentText(f"{h:02d}")
        self.hour.setFixedWidth(28)
        self.hour.setSizePolicy(QSizePolicy.Policy.Fixed,
                                QSizePolicy.Policy.Fixed)
        self.minute = SelectButton()
        self.minute.addItems([f"{i:02d}" for i in range(0, 60)])
        self.minute.setCurrentText(f"{mi:02d}")
        self.minute.setFixedWidth(28)
        self.minute.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.second = SelectButton()
        self.second.addItems([f"{i:02d}" for i in range(0, 60)])
        self.second.setCurrentText(f"{s:02d}")
        self.second.setFixedWidth(28)
        self.second.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def get(self):
        return format_interval(int(self.day.currentText()), int(self.hour.currentText()), int(self.minute.currentText()), int(self.second.currentText()))

    def widgets(self):
        return [QLabel(self.label), 'STRETCH', self.day, QLabel('天'), self.hour, QLabel(":"), self.minute, QLabel(":"), self.second]

    def update_gui(self, value):
        """更新GUI显示"""
        d, h, mi, s = parse_interval(value)
        self.day.setCurrentText(f"{d:02d}")
        self.hour.setCurrentText(f"{h:02d}")
        self.minute.setCurrentText(f"{mi:02d}")
        self.second.setCurrentText(f"{s:02d}")

class SchedulerSection(QGroupBox):
    def __init__(self, config, section_name):
        super().__init__("调度设置")
        self.config = config
        self.section_name = section_name
        self.scheduler = config[section_name].setdefault("scheduler", {
            "enable": False,
            "priority": 0,
            "next_run": "2023-01-01 00:00:00",
            "success_interval": "00:00:30:00",
            "failure_interval": "00:00:10:00",
        })
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        # 启用调度（CheckBox独占一行）
        self.enable_check = QCheckBox("启用调度")
        self.enable_check.setChecked(self.scheduler.get("enable", False))
        add_left_row(layout, [self.enable_check])

        # 优先级设置
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("优先级:"))
        self.priority = SelectButton()
        self.priority.addItems(["0", "1", "2", "3", "4", "5"])
        self.priority.setCurrentText(str(self.scheduler.get("priority", 0)))
        priority_layout.addWidget(self.priority)
        layout.addLayout(priority_layout)

        # 模式选择
        mode_layout = QHBoxLayout()
        self.time_radio = QRadioButton("定时执行")
        self.interval_radio = QRadioButton("间隔执行")
        mode = self.scheduler.get("mode", "time")
        self.time_radio.setChecked(mode == "time")
        self.interval_radio.setChecked(mode == "interval")
        self.time_radio.toggled.connect(self.on_mode_changed)
        self.interval_radio.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.time_radio)
        mode_layout.addWidget(self.interval_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # 时间设置
        self.time_edit = QTimeEdit()
        time_str = self.scheduler.get("time", "12:00:00")
        h, m, s = map(int, time_str.split(":"))
        self.time_edit.setTime(QTime(h, m, s))
        add_left_row(layout, [QLabel("执行时间"), self.time_edit])

        # 间隔时间设置
        self.interval_row = IntervalSelectRow(
            "执行间隔", self.scheduler.get("interval", "00:00:30:00"))
        add_left_row(layout, self.interval_row.widgets())

        # next_run 分段选择
        self.next_run_row = DateTimeSelectRow(
            "下次执行时间", self.scheduler.get("next_run", "2023-01-01 00:00:00"))
        add_left_row(layout, self.next_run_row.widgets())

        # success_interval 分段选择
        self.success_interval_row = IntervalSelectRow(
            "成功间隔时长", self.scheduler.get("success_interval", "00:00:30:00"))
        add_left_row(layout, self.success_interval_row.widgets())

        # failure_interval 分段选择
        self.failure_interval_row = IntervalSelectRow(
            "失败间隔时长", self.scheduler.get("failure_interval", "00:00:10:00"))
        add_left_row(layout, self.failure_interval_row.widgets())

        self.setLayout(layout)
        self.on_mode_changed()

    def on_mode_changed(self):
        """根据模式切换显示不同的控件"""
        is_time_mode = self.time_radio.isChecked()
        self.time_edit.setEnabled(is_time_mode)
        self.interval_row.widgets()[0].setEnabled(not is_time_mode)
        for widget in self.interval_row.widgets()[2:]:
            widget.setEnabled(not is_time_mode)

    def update_config(self):
        self.scheduler["enable"] = self.enable_check.isChecked()
        self.scheduler["priority"] = int(self.priority.currentText())
        self.scheduler["next_run"] = self.next_run_row.get()
        self.scheduler["success_interval"] = self.success_interval_row.get()
        self.scheduler["failure_interval"] = self.failure_interval_row.get()

    def update_gui(self):
        """更新GUI显示"""
        scheduler_config = self.config.get(
            self.section_name, {}).get("scheduler", {})

        # 更新启用状态
        self.enable_check.setChecked(scheduler_config.get("enable", False))

        # 更新优先级
        self.priority.setCurrentText(scheduler_config.get("priority", "0"))

        # 更新其他时间设置
        self.next_run_row.update_gui(
            scheduler_config.get("next_run", "2023-01-01 00:00:00"))
        self.success_interval_row.update_gui(
            scheduler_config.get("success_interval", "00:00:30:00"))
        self.failure_interval_row.update_gui(
            scheduler_config.get("failure_interval", "00:00:10:00"))

        # 更新控件状态
        self.on_mode_changed()
