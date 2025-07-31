from typing import Union
from tasks.task_base import TaskBase
from tasks.components.switch_souls.assets import SwitchSoulsAssets as SS
from tasks.main_page.routine import Routine

class SwitchSoul(TaskBase, SS):

    def switch_soul_one(self, group: int, team: int):
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
            1: self.C_SS_TEAM_TOP,
            2: self.C_SS_TEAM_MID,
            3: self.C_SS_TEAM_BOTTOM,
        }
        if group < 1 or group > 8:
            raise ValueError('Switch soul_one group must be in [1-8]')

        pass

    def switch_by_order(self, target: Union[tuple, list[tuple]]):
        if isinstance(target, tuple):
            target = [target]
        for group, team in target:
            group = int(group)
            team = int(team)
            self.switch_soul_one(group, team)
