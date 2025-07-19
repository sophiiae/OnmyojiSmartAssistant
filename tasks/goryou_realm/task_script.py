import time
import random
import numpy as np
from module.base.logger import logger
from tasks.battle.battle import Battle
from tasks.general.page import Page, page_exp, page_shikigami
from tasks.goryou_realm.assets import GoryouRealmAssets as GR
from module.base.exception import RequestHumanTakeover

class TaskScript(Battle, GR):

    def run(self):
        self.gr_config = self.config.model.goryou_realm.goryou_config

        self.wait_and_shot()
        if self.appear(self.I_GR_LV_3):
            self.click(self.I_GR_LV_3)

        self.toggle_realm_team_lock(
            self.gr_config.lock_team_enable)  # Lock team

        for c in range(400):
            logger.info(f"======== Round {c + 1} Exp Started =========")

            ramdon_sleep = random.randint(1, 100) / 100
            self.wait_and_shot(ramdon_sleep)

            if self.appear(self.I_GR_FIGHT):
                self.click(self.I_GR_FIGHT)
                self.run_battle()

    # def get_ticket_count(self):
    #     image = self.screenshot()
    #     count, total = self.O_TICKET_COUNT.digit_counter(image)
    #     return count


    def toggle_realm_team_lock(self, lock: bool = True):
        return self.toggle_team_lock(self.I_GR_TEAM_LOCK, self.I_GR_TEAM_UNLOCK, lock)
