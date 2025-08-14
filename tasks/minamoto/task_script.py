import time
from module.config.enums import BuffClass
from tasks.minamoto.assets import MinamotoAssets
from tasks.components.page.page import page_minamoto, page_main
from module.base.exception import TaskEnd
from tasks.components.battle.battle import Battle
from module.base.logger import logger

class TaskScript(MinamotoAssets, Battle):
    name = 'minamoto'

    def run(self):
        self.screenshot()
        if not self.appear(self.I_GHOST_ENT):
            if not self.check_page_appear(page_minamoto):
                self.goto(page_minamoto)

        self.guibing()  # 鬼兵演武
        # self.bingzang()  # 兵藏秘境

        self.goto(page_main, page_minamoto)
        raise TaskEnd(self.name)

    def enter_battle(self):
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_GHOST_CHALLENGE):
                break

            if self.appear_then_click(self.I_GHOST_CHALLENGE):
                continue

    def toggle_m_team_lock(self, lock: bool = True):
        return self.toggle_team_lock(self.I_TEAM_LOCK, self.I_TEAM_UNLOCK, lock)

    def guibing(self):
        # 进入鬼兵演武
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_GHOST_CHALLENGE):
                break

            if self.wait_until_appear(self.I_GHOST_ENT, 2):
                self.appear_then_click(self.I_GHOST_ENT)
                continue

        image = self.screenshot()
        level = self.O_GHOST_LEVEL.digit(image)
        self.toggle_m_team_lock()
        self.check_buff([BuffClass.EXP_100, BuffClass.EXP_50], page_minamoto)

        count = 0
        while level < 40:
            logger.info(f"======== Round Minamoto (level = {level}) =========")
            self.enter_battle()
            count += 1
            # if count % 10 == 0:
            #     time.sleep(0.3)
            #     image = self.screenshot()
            #     level = self.O_GHOST_LEVEL.digit(image)

            if not self.run_easy_battle(self.I_GHOST_CHALLENGE):
                break

        self.check_buff(
            [BuffClass.EXP_100_CLOSE, BuffClass.EXP_50_CLOSE], page_minamoto)

        # 满级了，结束
        self.appear_then_click(self.I_B_YELLOW_LEFT_ANGLE)

    def bingzang(self):
        # 兵藏秘境
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_BING_CHALLENGE):
                break

            if self.appear(self.I_BING_ENT):
                self.click(self.I_BING_ENT)
                continue
