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
            self.click(self.I_EXP_CHAPTER_28)
            count = self.colla_enter_chapter(max, count)

            # # 如果回到了探索界面 -> 检查宝箱
            # if self.wait_until_appear(self.I_C_EXP, 5):
            #     self.check_treasure_box()

        self.exit_task()

    def exit_task(self):
        time.sleep(1)
        while 1:
            self.wait_and_shot(0.3)
            if self.appear(GA.I_C_EXP):
                break

            if self.click_static_target(self.I_EXP_CHAPTER_DISMISS_ICON):
                continue

            # 确认退出章节
            if self.click_static_target(self.I_EXP_CHAPTER_EXIT_CONFIRM):
                continue

            # 退出章节
            if self.click_static_target(self.I_EXP_CHAPTER_EXIT):
                continue

        self.goto(page_main, page_exp)

    def colla_enter_chapter(self, max, count) -> int:
        # 点击 “探索” 按钮进入章节
        if not self.wait_until_appear(self.I_EXP_BUTTON):
            logger.error("Cannot find chapter exploration button")
            raise RequestHumanTakeover

        self.click_static_target(self.I_EXP_BUTTON)
        time.sleep(0.5)
        logger.info("Start battle...")
        c = count
        while 1:
            if c >= max:
                break

            if not self.wait_until_appear(self.I_EXP_C_CHAPTER, 1.5):
                logger.warning(
                    "***** Not inside chapter or battle finished.")
                raise RequestHumanTakeover

            # BOSS 挑战
            if self.appear(self.I_EXP_BOSS):
                self.click_moving_target(self.I_EXP_BOSS, self.I_BATTLE_CHECK)

                if self.run_battle():
                    c += 1
                    self.get_chapter_reward()
                    break
            # 普通怪挑战
            if self.click_moving_target(self.I_EXP_BATTLE, self.I_BATTLE_CHECK):
                if self.wait_until_appear(self.I_EXP_C_CHAPTER, 1):
                    continue
                c += 1
                self.run_battle()
            else:
                self.swipe(self.S_EXP_TO_RIGHT)

            time.sleep(0.3)
        return c
