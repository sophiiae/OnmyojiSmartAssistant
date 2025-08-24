import time
from module.base.exception import RequestHumanTakeover
from tasks.exploration.exp_base import ExpBase
from tasks.components.page.page import page_exp, page_main
from module.base.logger import logger
from tasks.general.assets import GeneralAssets as GA

class Colla(ExpBase):

    def start_colla(self, max_battle: int = 10):
        # 进入探索页面
        if not self.check_page_appear(page_exp):
            self.goto(page_exp)

        count = 0
        while count < max_battle:
            self.enter_colla_chapter()

            logger.info(f"======== Exp Chapter Entered =========")
            count, killed_boss = self.colla_chapter_battle(max_battle, count)

            if killed_boss:
                self.post_chapter_battle()

        self.exit_chapter()

    def enter_colla_chapter(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_EXP_CHAP_28, 0.98):
                break
            self.swipe(self.S_EXP_CHAPTER_UP)

        self.class_logger(self.name, "Entering chapter 28")
        if self.click_static_target(self.I_EXP_CHAP_28):
            self.click_static_target(self.I_EXP_BUTTON, 0.97, delay=1)

    def colla_chapter_battle(self, max, count) -> tuple:
        self.toggle_team_lock(self.I_EXP_TEAM_LOCK, self.I_EXP_TEAM_UNLOCK)

        c = count
        killed_boss = False
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
                    killed_boss = True
                    break

            # 普通怪挑战
            if self.appear(self.I_EXP_BATTLE):
                self.click_moving_target(
                    self.I_EXP_BATTLE, self.I_EXP_C_CHAPTER)
                self.run_easy_battle(self.I_EXP_C_CHAPTER)
                c += 1
                killed_boss = False
                continue

            else:
                self.swipe(self.S_EXP_TO_RIGHT)

            time.sleep(0.3)
        return c, killed_boss
