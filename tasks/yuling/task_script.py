import time
import random
import numpy as np
from module.base.logger import logger
from tasks.battle.battle import Battle
from tasks.general.page import Page, page_exp, page_shikigami
from tasks.yuling.assets import YulingAssets as YL
from module.base.exception import RequestHumanTakeover

class TaskScript(Battle, YL):

    def run(self):
        self.screenshot()
        if self.appear(self.I_YL_LV_3):
            self.click(self.I_YL_LV_3)

        for c in range(400):
            logger.info(f"======== Round {c + 1} Exp Started =========")

            ramdon_sleep = random.randint(1, 100) / 100
            self.wait_and_shot(ramdon_sleep)

            if self.appear(self.I_YL_FIGHT):
                self.click(self.I_YL_FIGHT)
                self.run_battle()

    # def get_ticket_count(self):
    #     image = self.screenshot()
    #     count, total = self.O_TICKET_COUNT.digit_counter(image)
    #     return count

    # def start_battle(self) -> bool:
    #     # 开始战斗
    #     while 1:
    #         time.sleep(0.4)
    #         self.screenshot()
    #         if not self.appear(self.I_SA_FIGHT_CHECK):
    #             break

    #         if self.appear(self.I_SA_FIGHT):
    #             self.click(self.I_SA_FIGHT)

    #     while 1:
    #         time.sleep(0.2)
    #         self.screenshot()
    #         if self.appear(self.I_SA_FIGHT_CHECK):
    #             return False

    #         # 只出现奖励宝箱
    #         if self.appear(self.I_REWARD):
    #             # 如果出现领奖励
    #             self.random_click_right()
    #             continue
