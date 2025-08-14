import time
import random
from module.base.exception import TaskEnd
from module.base.logger import logger
from tasks.components.battle.battle import Battle
from tasks.components.page.page import page_main, page_shikigami
from tasks.shikigami_activity.assets import ShikigamiActivityAssets as SA

"""
每月活动变动 （快速)
前提： 爬塔手动爬到10层/最高难度， 设置好队伍和御魂
1. 爬塔界面截图更新 sa_fight_check & sa_fight
2. py .\module\image_processing\assets_extractor.py 
3. 用 py ./match.py [script_name] [tupian] 更新坐标
4. 变更战斗次数，直接跑 py ./activity.py [config_name] 或者运行OSA
"""
class TaskScript(Battle, SA):
    name = "ShikigamiActivity"

    def run(self):
        self.sa_config = self.config.model.shikigami_activity.climb_config

        # 进入式神活动页面
        if not (self.appear(self.I_SA_FIGHT_CHECK) or self.check_page_appear(page_shikigami)):
            self.goto(page_shikigami)

        # 根据配置选择活动模式
        if self.sa_config.anniversary_mode:
            self.anniversary_battle()
        elif self.sa_config.demon_king_mode:
            self.demon_king()
        else:
            self.run_climb()

        # self.toggle_team_lock(self.I_SA_TEAM_LOCK, self.I_SA_TEAM_UNLOCK)

        # # 每天指定御魂不一样，不刷的话，就先关了这一块
        # ticket = self.get_ticket_count()
        # if ticket > 0:
        #     self.switch_mode(False)
        # for i in range(ticket):
        #     self.class_logger(self.name, f"======== Round {i + 1} by ticket =========")
        #     self.start_battle()

        # self.switch_mode()

        self.set_next_run(self.name, finish=True, success=True)
        self.goto(page_main, page_shikigami)
        raise TaskEnd(self.name)

    def run_climb(self):
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

        # 简单刷活动
        for i in range(self.sa_config.ticket_max):
            self.class_logger(
                self.name, f"======== Round {i + 1} by ticket =========")
            if not self.start_battle():
                break

    def anniversary_battle(self):
        # TODO: Need update
        self.class_logger(self.name, f"======== 周年庆 =========")

        # 用体力刷999
        count = self.sa_config.ticket_max
        while count:
            if count % 100 == 0:
                wait = random.randint(1, 60)
                self.class_logger(self.name, f"Random waiting time: {wait}")
                time.sleep(wait)

            self.class_logger(self.name,
                              f"======== Round {self.sa_config.ticket_max - count + 1} by AP ========")
            self.start_battle()
            count -= 1

    def demon_king(self):
        # TODO: Need update
        #  超鬼王
        while 1:
            self.class_logger(self.name, f"======== 超鬼王 ========")

            while 1:
                self.wait_and_shot()
                if self.appear(self.I_SA_BATTLE_CHECK):
                    break

                if self.appear_then_click(self.I_SA_SUMMON, 0.95):
                    self.class_logger(self.name, "召唤鬼王")
                    continue

                if self.appear_then_click(self.I_SA_SUMMON_FIGHT, 0.95):
                    continue

                self.appear_then_click(self.I_SA_BATTLE_READY, 0.95)

            while 1:
                self.class_logger(self.name, f"|||||||||| 战斗中 ||||||||||")
                self.wait_and_shot(1)
                if self.appear(self.I_SA_BATTLE_WIN):
                    # 出现胜利
                    self.click(self.battle_end_click)
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
                # 如果出现领奖励
                self.click(self.reward_click)
                continue
        return True

    def switch_mode(self, use_ep: bool = True):
        if use_ep:
            while 1:
                time.sleep(0.3)
                self.screenshot()
                if self.appear(self.I_SA_EP):
                    self.class_logger(self.name, "Using EP")
                    return True

                if self.appear(self.I_SA_TICKET):
                    self.wait_until_click(self.I_SA_SWITCH)

        if not use_ep:
            while 1:
                time.sleep(0.3)
                self.screenshot()
                if self.appear(self.I_SA_TICKET):
                    self.class_logger(self.name, "Using ticket")
                    return True

                if self.appear(self.I_SA_EP):
                    self.wait_until_click(self.I_SA_SWITCH)
