
import time
from module.base.logger import logger
from tasks.components.battle.battle import Battle
from tasks.components.page.page import page_boss, page_main
from tasks.area_boss.assets import AreaBossAssets
from module.base.exception import RequestHumanTakeover, TaskEnd

class TaskScript(Battle, AreaBossAssets):
    name = 'AreaBoss'

    def run(self):
        self.boss_config = self.config.model.area_boss.boss_config
        if not self.check_page_appear(page_boss):
            self.goto(page_boss)

        ss_config = self.config.model.area_boss.switch_soul_config
        ss_enable = ss_config.enable
        if ss_enable:
            self.run_switch_souls(
                self.I_AB_SHIKI_BOOK_ENT, ss_config.switch_group_team, self.I_C_BOSS)

        self.kill_top_bosses(self.boss_config.boss_number)

        self.set_next_run(task='AreaBoss', success=True, finish=False)
        self.goto(page_main, page_boss)
        raise TaskEnd(self.name)

    def open_kill_rank(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_AB_KILL_RANK_CHECK, 0.96):
                break

            self.appear_then_click(self.I_AB_BOSS_FILTER)

    def kill_top_bosses(self, boss_number):
        bosses = [
            self.I_AB_KILL_CHALLENGE_1,
            self.I_AB_KILL_CHALLENGE_2,
            self.I_AB_KILL_CHALLENGE_3
        ]

        for i in range(boss_number):
            self.open_kill_rank()
            self.kill_boss(bosses[i])

    def kill_boss(self, boss):
        # 普通难度
        while 1:
            self.wait_click_if_appear(boss)

            if self.appear_then_click(self.I_AB_REGULAR_HARDNESS):
                continue

            if self.appear(self.I_AB_BOSS_FIGHT):
                break

        # 地域鬼王等级降为1
        while 1:
            image = self.wait_and_shot()
            lv = self.O_AB_BOSS_LEVEL.digit(image)
            if lv == 1:
                break

            self.class_logger(self.name, f"Current area boss level: {lv}")
            if self.appear(self.I_AB_LV_ROLLER):
                sx, sy = self.I_AB_LV_ROLLER.roi_center()
                # 降为1
                self.device.swipe(sx, sy, 185, 284, 500)

        # 进入战斗
        while 1:
            self.wait_and_shot()
            if self.appear_then_click(self.I_AB_BOSS_FIGHT, delay=0.5):
                continue

            if not self.appear(self.I_AB_BOSS_FIGHT):
                break

        # 准备
        while 1:
            self.wait_and_shot(1)
            if not self.appear(self.I_AB_BOSS_READY, 0.95):
                break

            self.appear_then_click(self.I_AB_BOSS_READY, 0.95)

        self.run_boss_battle()
        self.exit_area_boss()

    def run_boss_battle(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_AB_BOSS_EXIT, 0.95):
                break

            self.appear_then_click(self.I_BATTLE_READY, 0.95)

            if self.appear(self.I_REWARD):
                self.get_reward()
                continue

            if self.appear(self.I_C_SHARE_PAGE):
                self.appear_then_click(self.I_SHARE_PAGE_EXIT)
                continue

            if self.appear(self.I_BATTLE_WIN, 0.95):
                self.click(self.battle_end_click)
            elif self.appear(self.I_BATTLE_FAILED, 0.95):
                self.click(self.battle_end_click)
                raise RequestHumanTakeover("Area Boss Battle Failed.")

    def exit_area_boss(self):
        # 退出BOSS挑战页面
        while 1:
            self.wait_and_shot()
            if self.appear_then_click(self.I_AB_BOSS_EXIT):
                continue

            if self.appear(self.I_C_BOSS):
                break
