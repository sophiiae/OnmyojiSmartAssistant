from module.base.exception import TaskEnd

from tasks.components.battle.battle import Battle
from tasks.components.page.page import page_guild, page_main
from tasks.netherworld.assets import NetherworldAssets

class TaskScript(Battle, NetherworldAssets):
    name = "Netherworld"

    def run(self):
        self.nw_config = self.config.model.netherworld
        # 进入寮页面
        if not self.check_page_appear(page_guild):
            self.goto(page_guild)

        self.screenshot()
        success = True
        if self.appear(self.I_NW_GUILD_ENT):
            self.run_nw()
        else:
            success = False

        self.set_next_run(self.name, finish=False, success=success)
        self.goto(page_main)
        raise TaskEnd(self.name)

    def run_nw(self):
        self.enter_nw_page()

        # 更换御魂
        ss_config = self.nw_config.switch_soul_config
        ss_enable = ss_config.enable

        if ss_enable:
            self.run_switch_souls(self.I_NW_SHIKI_BOOK_ENT,
                                  ss_config.switch_group_team,
                                  self.I_NW_ENT)
            # 重新进入页面
            self.enter_nw_page()

        # 进入组队页面
        while 1:
            self.class_logger(self.name, "Entering team up page.")
            self.wait_and_shot()
            if self.appear(self.I_NW_BATTLE_CHALLENGE, 0.96):
                break

            if self.appear_then_click(self.I_NW_BATTLE_CONFIRM, 0.95):
                continue

            self.appear_then_click(self.I_NW_CHALLENGE)

        # 开始战斗
        while 1:
            self.class_logger(self.name, "Start battle.")
            self.wait_and_shot()
            if self.appear(self.I_BATTLE_READY, 0.96):
                self.run_easy_battle(self.I_NW_ENT)
                break

            self.appear_then_click(self.I_NW_BATTLE_CHALLENGE)

        # 退出阴界页面
        while 1:
            self.class_logger(self.name, "Exit netherworld.")
            self.wait_and_shot()
            if self.appear(self.I_C_GUILD):
                break

            self.appear_then_click(self.I_NW_PAGE_EXIT)

    def enter_nw_page(self):
        self.class_logger(self.name, "Entering nw page.")
        # 进入阴界之门页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_NW_HEADER):
                break

            if self.appear_then_click(self.I_NW_ENT):
                continue

            self.appear_then_click(self.I_NW_GUILD_ENT)
