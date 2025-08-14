import random
import time
from module.base.logger import logger
from functools import cached_property
from module.config.enums import BuffClass
from module.image_processing.rule_image import RuleImage
from tasks.components.battle.assets import BattleAssets
from tasks.components.buff.buff import Buff
from tasks.components.page.page import Page
from tasks.components.page.page import page_main
from tasks.components.switch_souls.switch_souls import SwitchSouls
class Battle(Buff, SwitchSouls, BattleAssets):
    def run_easy_battle(self, exit_battle_check: RuleImage, failed_check: RuleImage | None = None) -> bool:
        logger.info("Start easy battle process")

        win = True

        while 1:
            self.wait_and_shot(0.4)
            if self.appear(exit_battle_check, 0.95):
                break

            self.appear_then_click(self.I_BATTLE_READY, 0.95)

            if self.appear(self.I_REWARD):
                self.get_reward()
                win = True
                continue

            if self.appear(self.I_BATTLE_WIN, 0.95):
                self.click(self.battle_end_click)
                win = True
                continue

            if failed_check and self.appear(failed_check, 0.95):
                self.click(self.battle_end_click)
                win = False
            elif self.appear(self.I_BATTLE_FAILED, 0.95):
                self.click(self.battle_end_click)
                win = False
        logger.info(f"** Got battle result: {win}")
        return win

    @cached_property
    def reward_click(self):
        return random.choice(
            [self.C_REWARD_1, self.C_REWARD_2])

    @cached_property
    def battle_end_click(self):
        return random.choice(
            [self.C_WIN_L, self.C_WIN_R])

    def get_reward(self):
        """领奖励
        """
        while 1:
            self.screenshot()
            if not self.appear(self.I_REWARD):
                break

            if self.appear(self.I_REWARD):
                self.click(self.reward_click)

    def run_battle_quit(self):
        """
        进入挑战然后直接退出
        :param config:
        :return:
        """
        # 退出
        while 1:
            self.wait_and_shot(0.5)
            if self.appear(self.I_BATTLE_FIGHT_AGAIN):
                break

            if self.appear_then_click(self.I_BATTLE_EXIT):
                time.sleep(0.3)
                self.appear_then_click(self.I_BATTLE_EXIT_CONFIRM, 0.3)
                continue

        logger.info("Clicked exit battle confirm")
        while 1:
            time.sleep(0.5)
            self.screenshot()
            if self.appear(self.I_BATTLE_FIGHT_AGAIN):
                self.click(self.battle_end_click)
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
            if self.appear_then_click(self.I_BATTLE_EXIT):
                continue
            if self.appear(self.I_BATTLE_EXIT_CONFIRM):
                break

        # 点击返回确认
        while 1:
            time.sleep(0.2)
            self.screenshot()
            if self.appear_then_click(self.I_BATTLE_EXIT_CONFIRM):
                continue
            if self.appear_then_click(self.I_BATTLE_FAILED):
                continue
            if not self.appear(self.I_BATTLE_EXIT):
                break

        return True

    def check_buff(self, buff: list[BuffClass] = [], page: Page = page_main):
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
            func, activate = match_buff[b]
            func(activate)
            time.sleep(0.1)

        logger.info(f'Open buff success')
        self.close_buff()

    def toggle_team_lock(self, team_lock: RuleImage, team_unlock: RuleImage, lock: bool = True):
        # 不锁定队伍
        while not lock:
            self.wait_and_shot()
            if self.appear(team_unlock, 0.95):
                return

            self.appear_then_click(team_lock)
            logger.info("Unlock the team")

        # 锁定队伍
        while lock:
            self.wait_and_shot()
            if self.appear(team_lock, 0.95):
                return

            self.appear_then_click(team_unlock)
            logger.info("Lock the team")

    def toggle_battle_auto(self):
        while 1:
            time.sleep(0.6)
            self.screenshot()
            if self.appear(self.I_BATTLE_AUTO):
                break

            if self.appear(self.I_BATTLE_MANUAL):
                self.click(self.I_BATTLE_MANUAL)
                continue

            if self.appear(self.I_BATTLE_WIN, 0.95):
                break
