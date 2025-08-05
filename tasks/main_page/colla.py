import time
from module.base.exception import RequestHumanTakeover
from tasks.exploration.task_script import TaskScript as EXP
from tasks.general.page import page_exp, page_main
from module.base.logger import logger
from tasks.general.assets import GeneralAssets as GA

class Colla(EXP):

    def start_colla(self):
        # 进入探索页面
        if not self.check_page_appear(page_exp):
            self.goto(page_exp)

        max = 10
        count = 0
        while count < max:
            self.enter_chap_28()

            logger.info(f"======== Exp Chapter Entered =========")
            count = self.colla_chapter_battle(max, count)

            self.after_chapter_battle()

        self.exit_chapter()
        self.goto(page_main)

    def colla_chapter_battle(self, max, count) -> int:
        if not self.wait_until_appear(self.I_EXP_C_CHAPTER, 2):
            logger.warning(
                "***** Not inside chapter or battle finished.")
            raise RequestHumanTakeover

        self.toggle_team_lock(self.I_EXP_TEAM_LOCK, self.I_EXP_TEAM_UNLOCK)

        c = count
        while 1:
            if c > max:
                break

            if c == max and not self.appear(self.I_EXP_BOSS):
                break

            self.screenshot()

            # BOSS 挑战
            if self.appear(self.I_EXP_BOSS):
                self.click_moving_target(self.I_EXP_BOSS, self.I_EXP_C_CHAPTER)

                if self.run_easy_battle(self.I_EXP_C_CHAPTER):
                    c += 1
                    self.get_chapter_reward()
                    break

            # 普通怪挑战
            if self.appear(self.I_EXP_BATTLE):
                self.click_moving_target(
                    self.I_EXP_BATTLE, self.I_EXP_C_CHAPTER)
                self.run_easy_battle(self.I_EXP_C_CHAPTER)
                c += 1
                continue

            else:
                self.swipe(self.S_EXP_TO_RIGHT)

            time.sleep(0.3)
        return c
