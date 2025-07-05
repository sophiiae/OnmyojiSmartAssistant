import random
import time
from venv import logger
from module.base.exception import TaskEnd
from tasks.battle.battle import Battle
from tasks.general.page import Page, page_exp, page_main
from tasks.royal_battle.assets import RoyalBattleAssets as RB

class TaskScript(Battle, RB):
    name = "Royal battle"
    current_level = 10
    levels = [2700, 2400, 2200, 2000, 1800]

    def run(self):
        self.screenshot()
        if not self.appear(self.I_RB_CHECK) and not self.appear(self.I_RB_CONTEST_CHECK):
            self.to_battle_entrance()

        reward_count = 0
        backward = 0
        # 如果掉过一次段位，下次上段位之后就不打了。 或者上了名士之后就不打了
        while 1 and self.current_level > 0:
            logger.info(f"======== Battle start =========")

            self.wait_and_shot(1)
            # if self.appear(self.I_RB_UPGRADE) or
            if self.appear(self.I_REWARD):
                self.random_click_right()

            if self.appear(self.I_RB_CHECK) or self.appear(self.I_RB_CONTEST_CHECK):
                # if self.appear(self.I_RB_FIGHT_BLUE):
                # level = self.get_level()
                # logger.info(
                #     f"### Battle: level={level}, backward: {backward}")

                # if level > self.current_level:  # 段位降低
                #     self.current_level = level
                #     backward += 1
                # elif level < self.current_level:  # 段位提升
                #     self.current_level = level
                #     if backward > 0:
                #         # 如果曾经掉过一次段位，就退出
                #         raise TaskEnd(self.name)
                if self.check_score(3000):
                    raise TaskEnd(self.name)

                self.battle_process()

        raise TaskEnd(self.name)

    # 斗技赛季模式
    def run_contest(self):
        self.screenshot()
        if not self.appear(self.I_RB_CONTEST_CHECK):
            self.to_battle_entrance()

        while 1 and self.current_level > 0:
            logger.info(f"======== Battle start =========")

            self.wait_and_shot(1)
            if self.appear(self.I_REWARD):
                self.random_click_right()

            if self.appear(self.I_RB_CONTEST_CHECK):
                if self.check_score(3000):
                    raise TaskEnd(self.name)

                self.battle_process(contest=True)

        raise TaskEnd(self.name)

    def check_score(self, target):
        image = self.screenshot()
        score = self.O_RB_SCORE.digit(image)
        return score >= target

    def get_level(self):
        image = self.screenshot()
        if self.appear(self.I_REWARD):
            self.get_reward()
            time.sleep(0.5)

        image = self.screenshot()
        score = self.O_RB_SCORE.digit(image)
        level = 5
        for lv, score_threshold in enumerate(self.levels):
            if score > score_threshold:
                level = lv
                break
        return level

    def to_battle_entrance(self):
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        self.go_to_daily_tasks_board()
        self.go_to_battle_page()

    def go_to_daily_tasks_board(self):
        # 进入日常界面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_RB_DAILY):
                break

            if self.appear(self.I_RB_ENT):
                self.click(self.I_RB_ENT)
            else:
                self.swipe(self.S_RB_TO_LEFT)

    def go_to_battle_page(self):
        # 进入斗技页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_RB_CHECK) or self.appear(self.I_RB_CONTEST_CHECK):
                break

            if self.appear(self.I_RB_GOTO):
                self.click(self.I_RB_GOTO)
                continue

            if self.appear(self.I_RB_LOGO):
                self.click(self.I_RB_LOGO)

    def battle_process(self, contest=False):
        time.sleep(1)
        if contest:
            while 1:
                self.wait_and_shot()
                if not self.appear(self.I_RB_CONTEST_CHECK):
                    break

                if self.appear(self.I_RB_CONTEST_FIGHT):
                    self.click(self.I_RB_CONTEST_FIGHT)
                    continue

                if self.appear(self.I_RB_FIGHT_BLUE):
                    self.click(self.I_RB_FIGHT_BLUE)
        else:
            self.start_battle()
        self.battle_ready()
        self.toggle_battle_auto()

        # 战斗
        while 1:
            self.wait_and_shot(1)
            action_click = random.choice(
                [self.C_WIN_1, self.C_WIN_2, self.C_WIN_3, self.C_WIN_4])
            if self.appear(self.I_BATTLE_WIN, 0.95):
                self.click(action_click)
                break

            if self.appear(self.I_RB_BATTLE_FAILED, 0.95):
                self.click(action_click)
                break

    def start_battle(self):
        count = 0
        # 开始斗技
        while 1:
            self.wait_and_shot(1)
            if self.appear(self.I_RB_TEAM_PREP_CHECK):
                break

            if self.appear(self.I_RB_CHECK) or self.appear(self.I_RB_CONTEST_CHECK):
                if self.appear(self.I_RB_FIGHT) or self.appear(self.I_RB_FIGHT_BLUE):
                    self.click(self.I_RB_FIGHT)
                    continue
            else:
                count += 1
                if count > 3:
                    raise TaskEnd(self.name)

    def battle_ready(self):
        # 开始斗技
        while 1:
            self.wait_and_shot(1)

            if self.appear(self.I_RB_TEAM_PREP_CHECK):
                # 开启自动上阵 (四段以上)
                if self.appear(self.I_RB_AUTO_TEAM):
                    self.click(self.I_RB_AUTO_TEAM)
                    break

            # 准备 （四段以下）
            if self.appear(self.I_RB_READY, 0.95):
                while 1:
                    self.wait_and_shot()
                    if not self.appear(self.I_RB_READY):
                        break
                    if self.appear(self.I_RB_READY):
                        self.click(self.I_RB_READY)
                break
