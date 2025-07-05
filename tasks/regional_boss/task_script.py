
import time
from tasks.battle.battle import Battle
from tasks.general.page import page_boss, page_main
from tasks.regional_boss.assets import RegionalBossAssets

class TaskScript(Battle, RegionalBossAssets):
    def run(self):
        if not self.check_page_appear(page_boss):
            self.goto(page_boss)
        self.kill_top_3_boss()
        self.goto(page_boss, page_main)

    def open_kill_rank(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_KILL_RANK_CHECK, 0.96):
                break

            if self.appear(self.I_BOSS_FILTER):
                self.click(self.I_BOSS_FILTER)

    def kill_top_3_boss(self):
        bosses = [
            self.I_KILL_CHALLENGE_1,
            self.I_KILL_CHALLENGE_2,
            self.I_KILL_CHALLENGE_3
        ]
        for boss in bosses:
            self.open_kill_rank()
            self.kill_boss(boss)

    def kill_boss(self, boss):
        while 1:
            self.wait_click_if_appear(boss)

            if self.appear(self.I_REGULAR_HARDNESS):
                self.click(self.I_REGULAR_HARDNESS)
                continue

            if self.appear(self.I_BOSS_FIGHT):
                break

        while 1:
            self.wait_and_shot()
            if self.appear(self.I_BOSS_FIGHT):
                self.click(self.I_BOSS_FIGHT)
                continue

            if not self.appear(self.I_BOSS_FIGHT):
                break

        while 1:
            self.wait_and_shot(1)
            if self.appear(self.I_BOSS_READY):
                self.click(self.I_BOSS_READY)
                continue

            if not self.appear(self.I_BOSS_READY):
                break

        self.run_battle()

        time.sleep(1)
        # 退出BOSS挑战页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_BOSS_EXIT):
                self.click(self.I_BOSS_EXIT)
                continue

            if self.appear(self.I_C_BOSS):
                break
