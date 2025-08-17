from functools import cached_property
import time

from module.base.logger import logger
from module.base.exception import RequestHumanTakeover
from module.image_processing.rule_image import RuleImage
from tasks.task_base import TaskBase
from tasks.components.page.page import page_login, page_main
from tasks.components.switch_account.assets import SwitchAccountAssets

class SwitchAccount(TaskBase, SwitchAccountAssets):
    name = "SwitchAccount"

    def enter_region(self):
        # TODO
        pass

    @cached_property
    def region_map(self):
        return {
            ("海外加速区", "全球国际区"): self.I_R_HAI_WAI_JIA_SU_QU,
            ("猫川别馆", "花火之夏", "神之晚宴"): self.I_R_MAO_CHUAN_BIE_GUAN,
            ("魔卡绮遇"): self.I_R_MO_KA_QI_YU,
            ("人间千年"): self.I_R_REN_JIAN_QIAN_NIAN,
            ("守山谣"): self.I_R_SHOU_SHAN_YAO,
            ("永生之海"): self.I_R_YONG_SHENG_ZHI_HAI,
            ("有龙则灵"): self.I_R_YOU_LONG_ZE_LING
        }

    def switch_account(self):
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        # 进入用户界面
        while 1:
            self.click(self.C_AVATAR)

            self.wait_and_shot()
            if self.appear(self.I_USER_CENTER):
                break

        # 返回登录页面
        while 1:
            time.sleep(0.5)
            self.screenshot()
            if self.appear_then_click(self.I_USER_CENTER):
                if self.wait_until_click(self.I_SWITCH_ACCOUNT, 2):
                    continue

            if self.appear_then_click(self.I_LOGIN):
                continue

            if self.appear_then_click(self.I_APPLE_LOGO):
                break

    def find_region(self, region: str):
        target = None
        for regions, img in self.region_map.items():
            if region in regions:
                target = img

        return target

    def switch_region(self, region: str):
        target = self.find_region(region)
        if target is None:
            raise RequestHumanTakeover(f"Not able to find region: {region}")

        self.screenshot()
        if not self.appear(self.I_C_LOGIN):
            raise RequestHumanTakeover("Not able to find login page")

        # 进入区域选择页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_OWN_CHARACTERS):
                break

            if self.appear(self.I_C_LOGIN) and not self.appear(self.I_PICK_REGION):
                self.click(self.C_REGION)
                continue

            if self.appear(self.I_PICK_REGION):
                if self.wait_until_click(self.I_OPEN_REGIONS, 2, delay=0.5):
                    continue

        # 选区
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_PICK_REGION):
                break

            if self.appear_then_click(target, 0.98):
                continue
            else:
                self.swipe(self.S_REGION_TO_LEFT, duration=500)
                time.sleep(0.5)

        # 登录游戏
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_MAIN, 0.95):
                logger.info("==>>> Arrive main page")
                break

            if self.appear(self.I_C_LOGIN):
                self.click(self.C_ENTER_GAME)
