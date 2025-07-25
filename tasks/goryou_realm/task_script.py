import time
import random
import numpy as np
from module.base.logger import logger
from tasks.battle.battle import Battle
from tasks.general.page import Page, page_goryou
from tasks.goryou_realm.assets import GoryouRealmAssets as GR
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.control.config.enums import GoryouClass

class TaskScript(Battle, GR):
    name = 'Goryou Realm'

    def run(self):
        self.gr_config = self.config.model.goryou_realm.goryou_config

        # 进入御灵页面
        if not self.appear(self.I_GR_FIGHT) and not self.check_page_appear(page_goryou):
            self.goto(page_goryou)

        goryou_class = self.gr_config.goryou_class
        lv = self.gr_config.level

        self.wait_and_shot()
        if self.appear(self.I_GR_LV_3):
            self.click(self.I_GR_LV_3)

        self.toggle_realm_team_lock(
            self.gr_config.lock_team_enable)  # Lock team

    def choose_class(self):
        match_click = {
            GoryouClass.Dark_Divine_Dragon: self.C_DARK_DIVINE_DRAGON,
            GoryouClass.Dark_Hakuzousu: self.C_DARK_HAKUZOUSU,
            GoryouClass.Dark_Black_Panther: self.C_DARK_BLACK_PANTHER,
            GoryouClass.Dark_Peacock: self.C_DARK_PEACOCK,
        }

        retry = 0
        while 1:
            if retry > 5:
                logger.error(
                    "Not abled to choose Goryou class. Please check the opening date for selected class.")
                raise TaskEnd(self.name)

            self.wait_and_shot()
            if self.appear(self.I_GR_FIGHT):
                logger.info("Entered Goryou fight page")
                break

            self.click(match_click[self.gr_config.goryou_class])
            retry += 1

    def choose_level(self):
        pass

    def start_battle(self):
        count_max = self.get_ticket_count()

        for c in range(count_max):
            logger.info(f"======== Round {c + 1} Exp Started =========")

            ramdon_sleep = random.randint(1, 100) / 100
            self.wait_and_shot(ramdon_sleep)

            if self.appear(self.I_GR_FIGHT):
                self.click(self.I_GR_FIGHT)
                self.run_battle()

    def get_ticket_count(self):
        image = self.screenshot()
        count = self.O_GR_TICKET_COUNT.digit(image)
        count_max = self.gr_config.count_max
        if count is None:
            raise RequestHumanTakeover("Failed to get ticket number.")

        if count > count_max:
            logger.warning(
                f"No enough tickets to support max round of battle. Will run battle for [{count}] times.")
        return count

    def toggle_realm_team_lock(self, lock: bool = True):
        return self.toggle_team_lock(self.I_GR_TEAM_LOCK, self.I_GR_TEAM_UNLOCK, lock)
