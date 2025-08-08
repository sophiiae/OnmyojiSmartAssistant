import time
import random
from module.base.logger import logger
from tasks.battle.battle import Battle
from tasks.general.page import Page, page_exp, page_shikigami
from tasks.shikigami_activity.assets import ShikigamiActivityAssets as SA
from module.base.exception import RequestHumanTakeover


"""
每月活动变动 （快速)
前提： 爬塔手动爬到10层/最高难度， 设置好队伍和御魂
1. 爬塔界面截图更新 sa_fight_check & sa_fight
2. py .\module\image_processing\assets_extractor.py 
3. 用 py ./match.py [script_name] [tupian] 更新坐标
4. 变更战斗次数，直接跑 py ./activity.py
"""
class TaskScript(Battle, SA):
    fight_count = 200  # 战斗次数

    def run(self):
        # 进入式神活动页面
        if not (self.appear(self.I_SA_FIGHT_CHECK) or self.check_page_appear(page_shikigami)):
            self.goto(page_shikigami)
            time.sleep(1)

        self.wait_and_shot()
        if not self.appear(self.I_SA_FIGHT_CHECK):
            # 进入爬塔页面
            while 1:
                self.wait_and_shot()
                if self.appear(self.I_SA_FIGHT_CHECK):
                    break

                if self.appear(self.I_SA_FIGHT_ENT, 0.95):
                    self.click(self.I_SA_FIGHT_ENT)
                    continue

        # self.toggle_team_lock(self.I_SA_TEAM_LOCK, self.I_SA_TEAM_UNLOCK)

        # # 每天指定御魂不一样，不刷的话，就先关了这一块
        # ticket = self.get_ticket_count()
        # if ticket > 0:
        #     self.switch_mode(False)
        # for i in range(ticket):
        #     logger.info(f"======== Round {i + 1} by ticket =========")
        #     self.start_battle()

        # self.switch_mode()

        # # 用体力刷999
        # count = 0
        # while count < 999:
        #     if count > 0 and count % 100 == 0:
        #         wait = np.random.randint(1, 200)
        #         logger.info(f"wating for {wait} seconds")
        #         time.sleep(wait)

        #     logger.info(f"======== Round {count + 1} by EP =========")
        #     self.start_battle()
        #     count += 1

        #     # if not self.wait_until_appear(self.I_SA_FIGHT_CHECK, 2):
        #     #     raise RequestHumanTakeover

        # # 返回庭院
        # while 1:
        #     time.sleep(0.3)
        #     self.screenshot()
        #     if self.appear(self.I_C_MAIN):
        #         break
        #     if self.appear(self.I_SA_EXIT):
        #         self.click(self.I_SA_EXIT)

        # 简单刷活动
        for i in range(self.fight_count):
            logger.info(f"======== Round {i + 1} by ticket =========")
            if not self.start_battle():
                break

        # self.guiwang()
        self.exit_activity()

    def guiwang(self):
        #  鬼王
        while 1:
            logger.info(f"======== 鬼王 =========")

            while 1:
                time.sleep(0.4)
                self.screenshot()
                if self.appear(self.I_SA_BATTLE_CHECK):
                    break

                if self.appear(self.I_SA_SUMMON, 0.95):
                    self.click(self.I_SA_SUMMON)
                    continue

                if self.appear(self.I_SA_SUMMON_FIGHT, 0.95):
                    self.click(self.I_SA_SUMMON_FIGHT)
                    continue

                if self.appear(self.I_SA_BATTLE_READY, 0.95):
                    self.click(self.I_SA_BATTLE_READY)

            while 1:
                logger.info(f"|||||||||| 战斗中 ||||||||||||")
                time.sleep(1)
                self.screenshot()
                if self.appear(self.I_SA_BATTLE_WIN):
                    # 出现胜利
                    action_click = random.choice(
                        [self.C_WIN_L, self.C_WIN_R])
                    self.click(action_click)
                    break

    def get_ticket_count(self):
        image = self.screenshot()
        count, total = self.O_TICKET_COUNT.digit_counter(image)
        return count

    def start_battle(self) -> bool:
        # 开始战斗
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_SA_FIGHT_CHECK):
                break

            if self.appear(self.I_SA_SHOP):
                self.click(self.I_SA_FIGHT)
                return False

            if self.appear(self.I_SA_FIGHT):
                self.click(self.I_SA_FIGHT)

        while 1:
            self.wait_and_shot(0.5)
            if self.appear(self.I_SA_FIGHT_CHECK):
                break

            # 只出现奖励宝箱
            if self.appear(self.I_SA_COIN, 0.95) or self.appear(self.I_REWARD):
                action_click = random.choice(
                    [self.C_REWARD_1, self.C_REWARD_2])
                # 如果出现领奖励
                self.click(action_click)
                continue
        return True

    def switch_mode(self, use_ep: bool = True):
        if use_ep:
            while 1:
                time.sleep(0.3)
                self.screenshot()
                if self.appear(self.I_SA_EP):
                    logger.info("Using EP")
                    return True

                if self.appear(self.I_SA_TICKET):
                    self.wait_until_click(self.I_SA_SWITCH)

        if not use_ep:
            while 1:
                time.sleep(0.3)
                self.screenshot()
                if self.appear(self.I_SA_TICKET):
                    logger.info("Using ticket")
                    return True

                if self.appear(self.I_SA_EP):
                    self.wait_until_click(self.I_SA_SWITCH)

    def exit_activity(self):
        retry = 0
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_MAIN, 0.95):
                break

            if retry > 10:
                raise RequestHumanTakeover()

            if self.appear(self.I_SA_EXIT):
                self.click(self.I_SA_EXIT)
                retry += 1
