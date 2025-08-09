from functools import cached_property
import random
import time
from venv import logger
from module.base.exception import TaskEnd
from module.config.enums import DuelRank, OnmyojiClass
from module.image_processing.rule_image import RuleImage
from tasks.battle.battle import Battle
from tasks.general.page import Page, page_dojo, page_main
from tasks.duel.assets import DuelAssets
from module.base.exception import RequestHumanTakeover

class TaskScript(Battle, DuelAssets):
    name = "Duel"
    contest_mode = False

    # 普通斗技模式 / 斗技赛季模式
    def run(self):
        self.rb_config = self.config.model.duel.duel_config
        self.screenshot()
        if not self.appear(self.page_check):
            self.to_battle_entrance()

        to_elite = self.rb_config.elite
        success = True
        if to_elite:
            success = self.battle_to_elite()
        else:
            success = self.rank_battle()

        self.set_next_run(task='Duel', success=success, finish=True)
        self.exit_duel()
        raise TaskEnd(self.name)

    @cached_property
    def page_check(self):
        return self.I_DUEL_CONTEST_CHECK if self.contest_mode else self.I_DUEL_CHECK

    @cached_property
    def rank_map(self):
        return {
            DuelRank.rank_1: 1001,
            DuelRank.rank_2: 1200,
            DuelRank.rank_3: 1400,
            DuelRank.rank_4: 1600,
            DuelRank.rank_5: 1800,
            DuelRank.rank_6: 2000,
            DuelRank.rank_7: 2200,
            DuelRank.rank_8: 2400,
            DuelRank.rank_9: 2700,
        }

    def battle_to_elite(self):
        retry = 0
        while 1:
            logger.info(f"======== Battle start =========")

            self.wait_and_shot(1)
            if self.appear(self.page_check):
                if self.appear(self.I_DUEL_NOTABLE_NOTIFICATION, 0.95) or self.appear(self.I_DUEL_NOTABLE_BADGE, 0.95):
                    return True

                if retry > 5:
                    return False

                if not self.appear(self.I_DUEL_FLOWER_BADGE):
                    self.random_click_right()
                    retry += 1
                    continue

                self.battle_process()
                retry = 0

    def rank_battle(self):
        target_rank = self.rb_config.rank
        target_score = self.rank_map[target_rank]
        if self.check_score(target_score):
            return True

        while 1:
            if self.appear(self.I_DUEL_FIGHT_BLUE, 0.985):
                if self.check_score(target_score):
                    return True

            self.battle_process()

    def check_score(self, target):
        image = self.screenshot()
        score = self.O_DUEL_SCORE.digit(image)
        self.class_logger(
            self.name, f"current score: {score}, target: {target}")
        return score > target

    def to_battle_entrance(self):
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        self.switch_souls_and_onmyoji()
        self.goto(page_dojo, page_main)

        while 1:
            self.wait_and_shot()
            if self.appear(self.page_check):
                break

            self.appear_then_click(self.I_DOJO_TO_DUEL)

    def switch_souls_and_onmyoji(self):
        ss_config = self.config.model.duel.switch_soul_config
        ss_enable = ss_config.enable

        # 换御魂
        if ss_enable:
            while 1:
                self.wait_and_shot()
                if self.appear(self.I_SCROLL_OPEN):
                    break

                if self.appear_then_click(self.I_SCROLL_CLOSE):
                    continue

            self.run_switch_souls(
                self.I_MAIN_SHIKI_BOOK_ENT, ss_config.switch_group_team, self.I_C_MAIN)

        # 换阴阳师
        onmyoji = self.rb_config.onmyoji
        if onmyoji == OnmyojiClass.AUTO:
            return

        self.change_onmyoji()

        # 返回庭院
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_MAIN, 0.96):
                break
            self.appear_then_click(self.I_EXIT_ONMYODO)

    def change_onmyoji(self):
        # 进入阴阳术
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_ONMYODO):
                break
            self.appear_then_click(self.I_MAIN_ONMYODO_ENT)

        assigned = self.rb_config.onmyoji
        # 交换类型
        if assigned == OnmyojiClass.Yorimitsu:
            self.change_onmyoji_type(self.I_HERO_SELECTED)
            return
        else:
            self.change_onmyoji_type(self.I_ONMYOJI_SELECTED)

        onmyoji_map = {
            OnmyojiClass.Seimei: self.C_SEIMEI,
            OnmyojiClass.Kagura: self.C_KAGURA,
            OnmyojiClass.Hiromasa: self.C_HIROMASA,
            OnmyojiClass.Yaobikuni: self.C_YAOBIKUNI
        }

        # 进入交换
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_CHANGE_PAGE):
                break

            self.appear_then_click(self.I_CHANGE_ONMYOJI)

        # 选择阴阳师
        retry = 0
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_ONMYODO, 0.96):
                retry = 0
                break

            if retry > 2:
                break

            self.click(onmyoji_map[assigned])
            retry += 1

        if retry > 0:
            while 1:
                self.wait_and_shot()
                if self.appear(self.I_C_ONMYODO, 0.96):
                    break
                self.appear_then_click(self.I_EXIT_CHANGE_PAGE)

    def change_onmyoji_type(self, target: RuleImage):
        while 1:
            self.wait_and_shot()
            if self.appear(target):
                break
            self.click(self.C_SWITCH_TYPE)

    def battle_process(self):
        time.sleep(1)
        self.class_logger(self.name, "==== Start battle process ====")
        if self.contest_mode:
            while 1:
                self.wait_and_shot()
                if not self.appear(self.page_check):
                    break

                if self.appear_then_click(self.I_DUEL_CONTEST_FIGHT):
                    continue

                self.appear_then_click(self.I_DUEL_FIGHT_BLUE)
        else:
            self.start_battle()

        self.battle_ready()
        self.toggle_battle_auto()
        self.run_easy_battle(self.page_check, self.I_DUEL_BATTLE_FAILED)

    def start_battle(self):
        count = 0
        # 开始斗技
        while 1:
            self.wait_and_shot(1)
            if self.appear(self.I_DUEL_TEAM_PREP_CHECK):
                break

            if self.appear(self.page_check):
                if self.appear(self.I_DUEL_FIGHT) or self.appear(self.I_DUEL_FIGHT_BLUE):
                    self.click(self.I_DUEL_FIGHT)
                    continue
            else:
                count += 1
                if count > 3:
                    raise RequestHumanTakeover("Unable to fight")

    def battle_ready(self):
        # 开始斗技
        while 1:
            self.wait_and_shot(1)

            if self.appear(self.I_DUEL_TEAM_PREP_CHECK):
                # 开启自动上阵 (四段以上)
                if self.appear_then_click(self.I_DUEL_AUTO_TEAM):
                    break

            # 准备 （四段以下）
            if self.appear(self.I_DUEL_READY, 0.95):
                while 1:
                    self.wait_and_shot()
                    if not self.appear(self.I_DUEL_READY):
                        break
                    self.appear_then_click(self.I_DUEL_READY)
                break

    def exit_duel(self):
        # 退出页面
        while 1:
            self.wait_and_shot()
            if not self.appear(self.page_check):
                break

            self.click(self.C_DUEL_EXIT)

        # 可能1： 从日常页面进入的斗技（手动进入）
        if self.appear(self.I_SCHEDULE_ICON, 0.95):
            while 1:
                self.wait_and_shot()
                if not self.appear(self.I_SCHEDULE_ICON):
                    break

                self.appear_then_click(self.I_SCHEDULE_CLOSE_X)

            # 回到庭院，左滑
            while 1:
                self.wait_and_shot()
                if self.appear(self.I_C_MAIN, 0.95):
                    return

                self.swipe(self.S_REGION_TO_LEFT)

        # 可能2： 从道馆进入（如果是脚本走的话）
        # 从到道馆回庭院
        if self.appear(self.I_C_DOJO):
            self.goto(page_main, page_dojo)
