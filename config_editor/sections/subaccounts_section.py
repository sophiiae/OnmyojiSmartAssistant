from PyQt6.QtWidgets import (QCheckBox, QDialog, QPushButton, QGroupBox, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QGridLayout)
from PyQt6.QtCore import Qt

from config_editor.sections.scheduler_section import SchedulerSection
from config_editor.utils import add_checkbox_right_row, add_left_row
from config_editor.widgets.value_button import ValueButton

class RegionsDialog(QDialog):
    def __init__(self, region="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑副设备")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 添加输入框
        self.region_edit = QLineEdit(region)
        layout.addWidget(QLabel("账号区服:"))
        layout.addWidget(self.region_edit)

        # 添加按钮
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("确定")
        self.cancel_button = QPushButton("取消")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setMinimumWidth(300)

class SubaccountsSection(QGroupBox):
    name = "subaccounts"

    def __init__(self, config):
        super().__init__("小号设置")
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        layout = QVBoxLayout(self)
        subaccounts_config = self.config[self.name]["subaccounts_config"]

        # 添加调度设置
        self.scheduler_section = SchedulerSection(
            self.config, self.name)
        layout.addWidget(self.scheduler_section)

        # 小号协战配置
        sub_group = QGroupBox("小号协战配置")
        sub_layout = QVBoxLayout(sub_group)

        # 账号区域设置
        subhost_layout = QHBoxLayout()  # 改为水平布局，让列表和按钮并列

        # 创建列表控件
        self.subhost_list = QListWidget()
        self.subhost_list.setMinimumHeight(100)
        self.subhost_list.setMaximumWidth(500)  # 限制列表最大宽度
        self.subhost_list.setSizeAdjustPolicy(
            QListWidget.SizeAdjustPolicy.AdjustToContents)
        self.subhost_list.addItems(subaccounts_config.get("regions", []))

        # 创建左侧垂直布局容器
        left_container = QVBoxLayout()
        left_container.addWidget(QLabel("账号区服列表: (第一个为默认区服)"))
        left_container.addWidget(self.subhost_list)
        subhost_layout.addLayout(left_container)

        # 添加按钮布局（改为垂直排列）
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("添加")
        self.edit_button = QPushButton("编辑")
        self.remove_button = QPushButton("删除")

        self.add_button.clicked.connect(self.add_region)
        self.edit_button.clicked.connect(self.edit_region)
        self.remove_button.clicked.connect(self.remove_subhost)

        button_layout.addStretch()  # 顶部弹性空间
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()  # 底部弹性空间，让按钮居中
        subhost_layout.addLayout(button_layout)

        sub_layout.addLayout(subhost_layout)

        # 启用协战模式（CheckBox独占一行）
        self.enable_collaboration = QCheckBox("启用协战模式(困28自动锁定队伍)")
        self.enable_collaboration.setChecked(
            subaccounts_config["enable_collaboration"])
        add_left_row(sub_layout, [self.enable_collaboration])

        # 协战次数（无CheckBox，左对齐）
        self.collaboration_count = ValueButton()
        self.collaboration_count.setRange(1, 15)
        self.collaboration_count.setValue(
            subaccounts_config["collaboration_count"])
        add_left_row(sub_layout, [QLabel("协战次数:"), self.collaboration_count])

        # 协战账号数量（无CheckBox，左对齐）
        self.collaboration_account_number = ValueButton()
        self.collaboration_account_number.setRange(0, 10)
        self.collaboration_account_number.setValue(
            subaccounts_config["collaboration_account_number"])
        add_left_row(sub_layout, [QLabel("协战账号数量:（前N个账号）"),
                     self.collaboration_account_number])

        # 启用日常任务（CheckBox独占一行）
        self.enable_daily_routine = QCheckBox("启用日常任务")
        self.enable_daily_routine.setChecked(
            subaccounts_config["enable_daily_routine"])
        add_left_row(sub_layout, [self.enable_daily_routine])

        layout.addWidget(sub_group)

        # 悬赏邀请配置
        invite_group = QGroupBox("悬赏邀请配置")
        invite_layout = QVBoxLayout(invite_group)

        # 邀请好友
        self.invite_quest_config = subaccounts_config["invite_quest_config"]

        # 启用悬赏邀请（CheckBox独占一行）
        self.enable_quest_invite = QCheckBox("启用悬赏邀请")
        self.enable_quest_invite.setChecked(
            self.invite_quest_config["enable_quest_invite"])

        # 邀请好友名称（无CheckBox，左对齐）
        self.invite_friend_name = QLineEdit()
        self.invite_friend_name.setText(
            self.invite_quest_config["invite_friend_name"])

        add_checkbox_right_row(invite_layout, self.enable_quest_invite, [
            QLabel("邀请好友名称:"), self.invite_friend_name])

        # 邀请任务类型
        grid = QGridLayout()

        self.invite_jade = QCheckBox("勾玉悬赏")
        self.invite_jade.setChecked(self.invite_quest_config["invite_jade"])
        grid.addWidget(self.invite_jade, 0, 0)

        self.invite_ap = QCheckBox("体力悬赏")
        self.invite_ap.setChecked(self.invite_quest_config["invite_ap"])
        grid.addWidget(self.invite_ap, 0, 1)

        self.invite_pet_food = QCheckBox("宠物粮悬赏")
        self.invite_pet_food.setChecked(
            self.invite_quest_config["invite_pet_food"])
        grid.addWidget(self.invite_pet_food, 0, 2)

        group = QGroupBox("邀请悬赏任务类型")
        group.setLayout(grid)
        invite_layout.addWidget(group)

        layout.addWidget(invite_group)

    def add_region(self):
        dialog = RegionsDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_subhost = dialog.region_edit.text().strip()
            if new_subhost:
                self.subhost_list.addItem(new_subhost)
                # 添加后立即更新配置
                self.update_config()

    def edit_region(self):
        current_item = self.subhost_list.currentItem()
        if current_item:
            dialog = RegionsDialog(current_item.text(), parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_subhost = dialog.region_edit.text().strip()
                if new_subhost:
                    current_item.setText(new_subhost)
                    # 编辑后立即更新配置
                    self.update_config()

    def remove_subhost(self):
        current_item = self.subhost_list.currentItem()
        if current_item:
            self.subhost_list.takeItem(self.subhost_list.row(current_item))
            # 删除后立即更新配置
            self.update_config()

    def update_config(self):
        self.scheduler_section.update_config()

        sa_config = self.config[self.name]["subaccounts_config"]
        sa_config["regions"] = []
        for i in range(self.subhost_list.count()):
            item = self.subhost_list.item(i)
            if item is not None:
                sa_config["regions"].append(item.text())
        sa_config["enable_collaboration"] = self.enable_collaboration.isChecked(
        )
        sa_config["collaboration_count"] = int(self.collaboration_count.text())
        sa_config["collaboration_account_number"] = self.collaboration_account_number.text()
        sa_config["enable_daily_routine"] = self.enable_daily_routine.isChecked(
        )

        invite_quest_config = sa_config["invite_quest_config"]
        invite_quest_config["enable_quest_invite"] = self.enable_quest_invite.isChecked(
        )
        invite_quest_config["invite_friend_name"] = self.invite_friend_name.text()
        invite_quest_config["invite_jade"] = self.invite_jade.isChecked()
        invite_quest_config["invite_ap"] = self.invite_ap.isChecked()
        invite_quest_config["invite_pet_food"] = self.invite_pet_food.isChecked()
        invite_quest_config["invite_friend_name"] = self.invite_friend_name.text()
