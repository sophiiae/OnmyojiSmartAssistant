from functools import cached_property
import time

from module.base.logger import logger
from module.base.exception import TaskEnd
from module.image_processing.rule_image import RuleImage
from tasks.components.page.page import page_main
from tasks.components.switch_account.switch_account import SwitchAccount
from tasks.daily_routine.task_script import TaskScript as DailyRoutine
from tasks.subaccounts.colla import Colla
from tasks.subaccounts.assets import SubaccountsAssets

class TaskScript(SwitchAccount, DailyRoutine, Colla, SubaccountsAssets):
    name = "Subaccounts"

    def run(self):
        self.sub_config = self.config.model.subaccounts.subaccounts_config
        self.colla_count = self.sub_config.collaboration_account_number
        regions_map = self.get_region_group(self.sub_config.regions)

        for region, count in regions_map.items():
            if count > 1:
                index = 0
                while index < count:
                    self.run_subaccount(region, index + 1)
                    index += 1
            else:
                self.run_subaccount(region)

        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        self.set_next_run(self.name, success=True, finish=True)
        raise TaskEnd(self.name)

    @cached_property
    def region_groups(self):
        return [
            ["海外加速区", "全球国际区"],
            ["猫川别馆", "花火之夏", "神之晚宴"],
            ["魔卡绮遇"],
            ["人间千年"],
            ["守山谣"],
            ["永生之海"],
            ["有龙则灵"]
        ]

    def get_region_group(self, regions: list):
        regions_map = {}

        for region in regions:
            for group in self.region_groups:
                if region in group:
                    regions_map[group[0]] = regions_map.get(group[0], 0) + 1
        logger.info(f"map: {regions_map}")
        return regions_map

    def run_subaccount(self, region: str, index: int = 0):
        self.switch_region(region, index)
        if self.sub_config.enable_daily_routine:
            self.check_shop_pack()
            self.check_harvest()

        if self.sub_config.invite_quest_config.enable_quest_invite:
            self.quest_invite()

        if self.sub_config.enable_collaboration:
            self.run_colla()

    def run_colla(self):
        if not self.colla_count:
            return
        max_count = self.sub_config.collaboration_count
        self.start_colla(max_count)
        self.colla_count -= 1

    @cached_property
    def plus_buttons(self):
        return [self.I_QUEST_PLUS_BUTTON_1, self.I_QUEST_PLUS_BUTTON_2, self.I_QUEST_PLUS_BUTTON_3]

    def quest_invite(self):
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        # 进去悬赏页面
        self.class_logger(self.name, "Entering quest page.")
        while 1:
            self.wait_and_shot()

            if self.appear(self.I_QUEST_HEADER):
                break

            self.appear_then_click(self.I_QUEST)

        self.check_quests()

    def check_quests(self):
        # 查看协作任务
        self.class_logger(self.name, "Checking quests.")
        self.invite_config = self.sub_config.invite_quest_config

        plus_button_list = [self.I_VIRTUAL_INVITE] + self.plus_buttons.copy()
        while plus_button_list:
            button = plus_button_list.pop(0)
            self.check_invite_quest(button)

        self.close_quest_board()

    def check_invite_quest(self, button: RuleImage):
        x_offset, y_offset, w, h = 30, 116, 190, 90

        self.wait_and_shot()
        if not self.appear(button, 0.96):
            return

        if self.appear(button, 0.97):
            self.class_logger(
                self.name, f"Checking invite quest type with button [{button.name}].")
            x, y = button.roi_center()
            nx, ny = x + x_offset, y + y_offset
            if self.invite_config.invite_jade:
                self.I_QUEST_JADE.set_area(nx, ny, w, h)
                if self.appear(self.I_QUEST_JADE):
                    self.invite_friend(button)
                    return

            if self.invite_config.invite_ap:
                self.I_QUEST_AP.set_area(nx, ny, w, h)
                if self.appear(self.I_QUEST_AP):
                    self.invite_friend(button)
                    return

            if self.invite_config.invite_pet_food:
                self.I_QUEST_CAT.set_area(nx, ny, w, h)
                self.I_QUEST_DOG.set_area(nx, ny, w, h)
                if self.appear(self.I_QUEST_CAT) or self.appear(self.I_QUEST_DOG):
                    self.invite_friend(button)
                    return

    def invite_friend(self, button: RuleImage):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_INVITE, 0.96):
                break

            self.click(button)

        self.class_logger(self.name, "Invite friend.")
        retry = 0
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_AVATAR, 0.96):
                retry = 0
                break

            if retry > 3:
                self.appear_then_click(self.I_CANCEL_INVITE)
                break

            if self.appear_then_click(self.I_CROSS_REGION_DISABLED, 0.96):
                continue

            self.click(self.C_SAME_REGION_FRIENDS)

        if retry > 0:
            self.close_quest_board()
        else:
            self.send_invitation()

    def send_invitation(self,):
        x, y = self.I_AVATAR.roi_center_random()

        # 选择好友
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_AVATAR_SELECTED, 0.97):
                break

            self.appear_then_click(self.I_AVATAR)

        # 邀请
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_INVITE):
                break

            self.appear_then_click(self.I_INVITE)

        self.close_quest_board()

    def close_quest_board(self):
        # 关闭悬赏页面
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_QUEST_HEADER):
                break
            self.appear_then_click(self.I_CLOSE_QUEST_BOARD)
