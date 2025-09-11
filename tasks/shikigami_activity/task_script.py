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
        if not (self.appear(self.I_SA_FIGHT_PAGE_CHECK) or self.appear(self.I_SA_FIGHT_TARGET_PAGE_CHECK) or self.check_page_appear(page_shikigami)):
            self.goto(page_shikigami)

        # 根据配置选择活动模式
        if self.sa_config.anniversary_mode:
            self.anniversary_battle()
        elif self.sa_config.demon_king_mode:
            self.demon_king()
        else:
            self.run_climb()

        self.set_next_run(self.name, finish=True, success=True)
        self.exit_activity()
        raise TaskEnd(self.name)

    def run_climb(self):
        self.wait_and_shot()
        if not self.appear(self.I_SA_FIGHT_PAGE_CHECK):
            # 进入爬塔页面
            while 1:
                self.wait_and_shot()
                if self.appear(self.I_SA_FIGHT_PAGE_CHECK):
                    break

                if self.appear(self.I_SA_FIGHT_PAGE_ENT, 0.95):
                    self.click(self.I_SA_FIGHT_PAGE_ENT)
                    continue

        # 简单刷活动
        for i in range(self.sa_config.ticket_max):
            self.class_logger(
                self.name, f"======== Round {i + 1} by ticket =========")
            if not self.start_battle():
                break

    def anniversary_battle(self):
        self.class_logger(self.name, f"======== 周年庆 =========")
        self.anni_enter_fight_page()
        # self.toggle_team_lock(self.I_SA_TEAM_LOCK, self.I_SA_TEAM_UNLOCK)
        self.change_souls()

        # 每天指定御魂不一样，不刷的话，就先关了体力模式
        self.switch_mode()
        use_ap = self.sa_config.enable_ap_mode
        count = self.get_ticket_count()
        if use_ap:
            # 用体力刷999
            count = self.anni_ticket_count()

        while count:
            if count // 100 == 0:
                wait = random.randint(1, 30)
                self.class_logger(self.name, f"Random waiting time: {wait}")
                time.sleep(wait)

            self.class_logger(self.name,
                              f"======== Round {count} by AP ========")
            self.start_battle()
            count -= 1

    def change_souls(self):
        # 更换御魂
        ss_config = self.config.model.shikigami_activity.switch_soul_config
        ss_enable = ss_config.enable

        if ss_enable:
            self.run_switch_souls(self.I_SA_SHIKI_BOOK_ENT,
                                  ss_config.switch_group_team,
                                  self.I_SA_FIGHT_TARGET_PAGE_CHECK)

    def anni_ticket_count(self):
        image = self.screenshot()
        ap_max = self.sa_config.ap_max
        count, total = self.O_ANIVERSARY_TICKET_COUNT.digit_counter(image)
        return count if count < ap_max else ap_max

    def anni_enter_fight_page(self):
        if self.appear(self.I_SA_FIGHT_TARGET_PAGE_CHECK):
            return

        # 进入战斗页面
        while 1:
            self.class_logger(self.name, "Entering fight page.")
            self.wait_and_shot()
            if self.appear(self.I_SA_FIGHT_PAGE_CHECK):
                break

            self.appear_then_click(self.I_SA_FIGHT_PAGE_ENT)

        # 进入目标战斗页面
        while 1:
            self.class_logger(self.name, "Entering battle(fight target) page.")
            self.wait_and_shot()
            if self.appear(self.I_SA_FIGHT_TARGET_PAGE_CHECK):
                break

            self.appear_then_click(self.I_SA_FIGHT_TARGET)

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
        ticket_max = self.sa_config.ticket_max
        count = self.O_TICKET_COUNT.digit(image)
        return count if count < ticket_max else ticket_max

    def start_battle(self) -> bool:
        # 开始战斗
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_SA_FIGHT_TARGET_PAGE_CHECK):
                break

            if self.appear(self.I_SA_SHOP):
                self.click(self.I_SA_FIGHT)
                return False

            self.appear_then_click(self.I_SA_FIGHT)

        while 1:
            self.wait_and_shot(0.5)
            if self.appear(self.I_SA_FIGHT_TARGET_PAGE_CHECK):
                break

            # 只出现奖励宝箱
            if self.appear(self.I_SA_COIN, 0.95) or self.appear(self.I_REWARD) or self.appear(self.I_GAIN_REWARD):
                # 如果出现领奖励
                self.click(self.reward_click)
                continue
        return True

    def switch_mode(self, use_ap: bool = True):
        use_ap = self.sa_config.enable_ap_mode
        if use_ap:
            self.class_logger(self.name, "Enable AP mode.")
            while 1:
                self.wait_and_shot()
                if self.appear(self.I_SA_AP):
                    self.class_logger(self.name, "Using AP")
                    return True

                if self.appear(self.I_SA_TICKET):
                    self.wait_until_click(self.I_SA_SWITCH)

        if not use_ap:
            self.class_logger(self.name, "Enable ticket mode.")
            while 1:
                self.wait_and_shot()
                if self.appear(self.I_SA_TICKET):
                    self.class_logger(self.name, "Using ticket")
                    return True

                if self.appear(self.I_SA_AP):
                    self.wait_until_click(self.I_SA_SWITCH)

    def exit_activity(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_SA_MAIN_ENT, 0.96):
                break

            self.appear_then_click(self.I_SA_EXIT)
