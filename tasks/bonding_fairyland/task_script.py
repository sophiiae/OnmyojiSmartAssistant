from module.base.exception import TaskEnd
from tasks.components.battle.battle import Battle
from tasks.bonding_fairyland.assets import BondingFairylandAssets as BFA
from tasks.components.page.page import page_bonding_fairyland

class TaskScript(Battle, BFA):
    name = "BondingFairyland"

    def run(self):
        if not self.check_page_appear(page_bonding_fairyland):
            self.goto(page_bonding_fairyland)

        self.bf_config = self.config.model.bonding_fairyland

        ss_config = self.bf_config.switch_soul_config
        ss_enable = ss_config.enable

        if ss_enable:
            self.run_switch_souls(self.I_BF_SHIKI_BOOK_ENT,
                                  ss_config.switch_group_team,
                                  self.I_C_FAIRYLAND)

        self.toggle_bf_lock(self.bf_config.bonding_config.lock_team_enable)

        explore_count = self.bf_config.bonding_config.explore_count
        self.class_logger(self.name, f"Explore times: {explore_count}")

        success = True
        count = 0
        while count < explore_count:
            self.class_logger(self.name,
                              f"======== Round {count + 1} Bonding Explore =========")
            self.wait_and_shot()
            if self.appear(self.I_BF_EXPLORE):
                self.click_static_target(self.I_BF_EXPLORE)
                if self.run_easy_battle(self.I_C_FAIRYLAND):
                    count += 1
                else:
                    success = False
                    break

        self.set_next_run(task=self.name, success=success, finish=True)
        raise TaskEnd(self.name)

    def toggle_bf_lock(self, lock: bool = True):
        return self.toggle_team_lock(self.I_BF_TEAM_LOCK, self.I_BF_TEAM_UNLOCK, lock)
