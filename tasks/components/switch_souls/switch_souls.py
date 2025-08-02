from typing import Union
import time
import math
from tasks.task_base import TaskBase
from tasks.components.switch_souls.assets import SwitchSoulsAssets as SS
from module.base.logger import logger
from module.image_processing.rule_image import RuleImage

class SwitchSouls(TaskBase, SS):
    name = 'SwitchSouls'

    def enter_shiki_book(self, shiki_book_ent: RuleImage):
        # 进入式神录
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_SHIKI_BOOK_CHECK, 0.95):
                break

            if self.appear(shiki_book_ent, 0.95):
                self.click(shiki_book_ent)

    def run_switch_souls(self, shiki_book_ent: RuleImage, target: str, page_check: RuleImage):
        self.enter_shiki_book(shiki_book_ent)

        # 打开预设页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_SS_PRESET_CHECK):
                break

            self.click(self.C_SS_OPEN_PRESET)

        parsed_target = self.switch_parser(target)
        self.switch_souls(parsed_target)

        self.exit_shiki_book(page_check)

    def exit_shiki_book(self, page_check):
        # 退出式神录
        while 1:
            self.class_logger(self.name, "Back to page")
            self.wait_and_shot()
            if self.appear(page_check, 0.95):
                break

            if self.appear(self.I_SHIKI_SOUL_EXIT):
                self.click(self.I_SHIKI_SOUL_EXIT)

    def switch_soul_one(self, group: int, team: int, first_time: bool = False):
        match_group = {
            1: self.I_SS_GROUP_1,
            2: self.I_SS_GROUP_2,
            3: self.I_SS_GROUP_3,
            4: self.I_SS_GROUP_4,
            5: self.I_SS_GROUP_5,
            6: self.I_SS_GROUP_6,
            7: self.I_SS_GROUP_7,
            8: self.I_SS_GROUP_8,
        }
        match_team = {
            1: self.I_SS_SWITCH_SOUL_TOP,
            2: self.I_SS_SWITCH_SOUL_MID,
            3: self.I_SS_SWITCH_SOUL_BOTTOM,
        }
        if group < 1 or group > 8 or team < 1:
            raise ValueError(
                'Switch soul_one group must be in [1-8] and team must be greater than 0')

        if first_time:
            # 第一次换之前先把组往下拉，让第一组在最上面
            self.swipe(self.S_SS_GROUP_DOWN, duration=500)
            time.sleep(0.6)

        group_target = match_group[group]

        # 选择组
        while 1:
            self.class_logger(self.name, f"Choose group {group}")
            self.click(group_target)

            self.wait_and_shot()
            if self.appear(group_target):
                break

        # 替换队伍御魂
        if team > 3:
            swipe_times = team // 3
            self.class_logger(self.name,
                              f"going to swipe team up for {swipe_times} times")
            for i in range(swipe_times):
                self.class_logger(self.name,
                                  f"swipe team up for {i + 1} time")
                self.swipe(self.S_SS_TEAM_UP, duration=500)
                time.sleep(1)

        team_order = team % 3
        team_order = 3 if team_order == 0 else team_order

        # 更换队伍御魂
        while 1:
            self.class_logger(self.name, f"Switch souls for team {team_order}")
            target_team_switch = match_team[team_order]
            self.wait_and_shot()

            if self.appear(target_team_switch):
                self.click(target_team_switch)
                break

        # 确定更换
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_SS_CONFIRM, 0.95):
                break

            if self.appear(self.I_SS_CONFIRM, 0.95):
                self.click(self.I_SS_CONFIRM)

    def switch_souls(self, target: Union[tuple, list[tuple]]):
        if isinstance(target, tuple):
            target = [target]

        i = 0
        for group, team in target:
            group = int(group)
            team = int(team)
            self.switch_soul_one(group, team, i == 0)
            i += 1

    def switch_parser(self, target: str) -> list[tuple[int, int]]:
        if target == "":
            return []
        result = []
        for group_team in target.split(';'):
            parts = group_team.split(',')
            if len(parts) == 2:
                result.append((int(parts[0]), int(parts[1])))
        return result

    def class_logger(self, task: str, message: str):
        logger.info(f"*{task}* {message}")
