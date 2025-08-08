
import time
from tasks.battle.battle import Battle
from tasks.general.page import page_boss, page_main
from tasks.area_boss.assets import AreaBossAssets
from module.base.exception import TaskEnd

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

        self.set_next_run(task='AreaBoss', success=True, finish=True)
        self.goto(page_main, page_boss)
        raise TaskEnd(self.name)

    def open_kill_rank(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_AB_KILL_RANK_CHECK, 0.96):
                break

            if self.appear(self.I_AB_BOSS_FILTER):
                self.click(self.I_AB_BOSS_FILTER)

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

            if self.appear(self.I_AB_REGULAR_HARDNESS):
                self.click(self.I_AB_REGULAR_HARDNESS)
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
            if self.appear(self.I_AB_BOSS_FIGHT):
                self.click(self.I_AB_BOSS_FIGHT)
                continue

            if not self.appear(self.I_AB_BOSS_FIGHT):
                break

        while 1:
            self.wait_and_shot(1)
            if self.appear(self.I_AB_BOSS_READY):
                self.click(self.I_AB_BOSS_READY)
                continue

            if not self.appear(self.I_AB_BOSS_READY):
                break

        self.run_battle()

        time.sleep(1)
        # 退出BOSS挑战页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_AB_BOSS_EXIT):
                self.click(self.I_AB_BOSS_EXIT)
                continue

            if self.appear(self.I_C_BOSS):
                break
