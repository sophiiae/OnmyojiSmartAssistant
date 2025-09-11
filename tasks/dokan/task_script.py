from module.base.exception import TaskEnd
from tasks.dokan.assets import DokanAssets
from tasks.components.battle.battle import Battle
from tasks.components.page.page import page_guild, page_main

class TaskScript(Battle, DokanAssets):
    name = "Dokan"

    def run(self):
        self.dk_config = self.config.model.dokan

        # 进入寮页面
        if not self.check_page_appear(page_guild):
            self.goto(page_guild)

        self.screenshot()
        success = True
        if self.appear(self.I_DK_GUILD_ENT, 0.96):
            self.enter_dk_page()
            self.run_dk()
            self.exit_dk()
        else:
            success = False

        self.set_next_run(self.name, finish=False, success=success)
        self.goto(page_main)
        raise TaskEnd(self.name)

    def enter_dk_page(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_DK_MAP_CHECK):
                break

            self.appear_then_click(self.I_DK_GUILD_ENT)

        while 1:
            self.wait_and_shot()
            if self.appear(self.I_DK_PAGE_HEADER):
                break

            self.appear_then_click(self.I_TARGET_DOKAN, 0.95)

    def run_dk(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_DK_CHALLENGE):
                self.start_battle()

            if self.appear(self.I_DK_WIN_LARGE):
                self.click(self.C_WIN_BLANK)
                break

            if self.appear(self.I_DK_CONQUER_SWORD) or self.appear(self.I_DK_WIN_SMALL):
                self.click(self.C_WIN_BLANK)

    def start_battle(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_BATTLE_READY):
                self.run_dk_battle()
                break

            self.appear_then_click(self.I_DK_CHALLENGE)

    def run_dk_battle(self):
        self.class_logger(self.name, "Start dokan battle process")
        win = True

        while 1:
            self.wait_and_shot(0.4)
            if self.appear(self.I_DK_PAGE_HEADER, 0.95):
                break

            if self.appear_then_click(self.I_BATTLE_READY, 0.95):
                self.click(self.C_SHIKI_LEFT_1)

            if self.appear(self.I_REWARD):
                self.get_reward()
                win = True
                continue

            if self.appear(self.I_BATTLE_WIN, 0.95):
                self.click(self.battle_end_click)
                win = True
                continue

            if self.appear(self.I_BATTLE_FAILED, 0.95):
                self.click(self.battle_end_click)
                win = False
        self.class_logger(self.name, f"** Got battle result: {win}")
        return win

    def exit_dk(self):
        while 1:
            self.wait_and_shot()
            if self.check_page_appear(page_guild):
                break

            if self.appear_then_click(self.I_DK_MAP_EXIT):
                continue

            if self.appear_then_click(self.I_DK_EXIT_CONFIRM, 0.96):
                continue

            self.appear_then_click(self.I_DK_DOKAN_EXIT)
