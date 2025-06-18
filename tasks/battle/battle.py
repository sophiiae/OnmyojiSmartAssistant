import random
import time
from module.base.logger import logger
from module.base.timer import Timer
from module.control.config.enums import BuffClass
from module.image_processing.rule_image import RuleImage
from tasks.battle.assets import BattleAssets
from tasks.buff.buff import Buff
from tasks.general.page import Page
from tasks.task_base import TaskBase
from module.base.exception import RequestHumanTakeover
from tasks.general.general import General
from tasks.general.page import page_main

class Battle(General, Buff, BattleAssets):

    def run_battle(self) -> bool:
        logger.info("Start battle process")
        win = False

        while 1:
            time.sleep(0.4)
            self.screenshot()

            if self.appear(self.I_BATTLE_WIN):
                win = True
                break

            if self.appear(self.I_REWARD):
                win = True
                break

            if self.appear(self.I_BATTLE_FIGHT_AGAIN):
                break

        logger.info(f"** Got battle result: {win}")
        if not win:
            action_click = random.choice(
                [self.C_WIN_1, self.C_WIN_2, self.C_WIN_3, self.C_WIN_4])
            self.click(action_click)
            return win

        logger.info("Get reward")
        timeout = Timer(5, 5).start()
        got_reward = False
        while 1:
            if timeout.reached():
                break

            self.screenshot()
            if got_reward and not self.appear(self.I_REWARD):
                break

            if self.get_reward():
                got_reward = True
                continue

            if self.appear(self.I_BATTLE_WIN):
                action_click = random.choice(
                    [self.C_REWARD_1, self.C_REWARD_2])
                self.click(action_click)

        time.sleep(1)
        return win

    def get_reward(self):
        """领奖励
        """
        self.screenshot()
        if self.appear(self.I_REWARD):
            action_click = random.choice(
                [self.C_REWARD_1, self.C_REWARD_2])
            self.click(action_click)
            return True
        return False

    def run_battle_quit(self):
        """
        进入挑战然后直接退出
        :param config:
        :return:
        """
        # 退出
        while 1:
            time.sleep(1)
            self.screenshot()
            if self.appear(self.I_BATTLE_FIGHT_AGAIN):
                break

            if self.click_static_target(self.I_BATTLE_EXIT):
                self.click_static_target(self.I_BATTLE_EXIT_CONFIRM)
                continue

        logger.info("Clicked exit battle confirm")
        while 1:
            time.sleep(0.5)
            self.screenshot()
            if self.appear(self.I_BATTLE_FIGHT_AGAIN):
                action_click = random.choice(
                    [self.C_WIN_1, self.C_WIN_2, self.C_WIN_3, self.C_WIN_4])
                self.click(action_click)
                continue

            if not self.appear(self.I_BATTLE_FIGHT_AGAIN):
                break

        return True

    def exit_battle(self) -> bool:
        self.screenshot()

        if not self.appear(self.I_BATTLE_EXIT):
            return False

        # 点击返回
        logger.info(f"Click {self.I_BATTLE_EXIT.name}")
        while 1:
            time.sleep(0.2)
            self.screenshot()
            if self.click_static_target(self.I_BATTLE_EXIT):
                continue
            if self.appear(self.I_BATTLE_EXIT_CONFIRM):
                break

        # 点击返回确认
        while 1:
            time.sleep(0.2)
            self.screenshot()
            if self.click_static_target(self.I_BATTLE_EXIT_CONFIRM):
                continue
            if self.click_static_target(self.I_BATTLE_FAILED):
                continue
            if not self.appear(self.I_BATTLE_EXIT):
                break

        return True

    def check_buff(self, buff: list[BuffClass], page: Page = page_main):
        if not buff:
            return

        match_buff = {
            BuffClass.AWAKE: (self.awake, True),
            BuffClass.SOUL: (self.soul, True),
            BuffClass.GOLD_50: (self.gold_50, True),
            BuffClass.GOLD_100: (self.gold_100, True),
            BuffClass.EXP_50: (self.exp_50, True),
            BuffClass.EXP_100: (self.exp_100, True),
            BuffClass.AWAKE_CLOSE: (self.awake, False),
            BuffClass.SOUL_CLOSE: (self.soul, False),
            BuffClass.GOLD_50_CLOSE: (self.gold_50, False),
            BuffClass.GOLD_100_CLOSE: (self.gold_100, False),
            BuffClass.EXP_50_CLOSE: (self.exp_50, False),
            BuffClass.EXP_100_CLOSE: (self.exp_100, False),
        }

        self.open_buff(page)
        for b in buff:
            func, is_open = match_buff[b]
            func(is_open)
            time.sleep(0.1)

        logger.info(f'Open buff success')
        self.close_buff()

    def toggle_team_lock(self, team_lock: RuleImage, team_unlock: RuleImage, is_lock: bool = True):
        # 锁定队伍
        if not is_lock:
            if self.wait_until_appear(team_lock, 1):
                self.click_static_target(team_lock)
                logger.info("Unlock the team")
                return True

        # 不锁定队伍
        if is_lock:
            if self.wait_until_appear(team_unlock, 1):
                self.click_static_target(team_unlock)
                logger.info("Lock the team")
                return True

        return False

    def toggle_battle_auto(self):
        while 1:
            time.sleep(0.6)
            self.screenshot()
            if self.appear(self.I_BATTLE_AUTO):
                break

            if self.click_static_target(self.I_BATTLE_MANUAL):
                continue

            if self.appear(self.I_BATTLE_WIN, 0.95):
                break
