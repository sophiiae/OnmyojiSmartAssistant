import sys
from module.control.server.device import Device
from tasks.subaccounts.task_script import TaskScript as TS
from tasks.duel.task_script import TaskScript as RB
from module.base.logger import logger


def RunTaskTest(name):
    d = Device(config_name=name)
    dr = TS(device=d)
    regions = ["海外加速区",
               "猫川别馆", "花火之夏", "神之晚宴",
               "魔卡绮遇",
               "人间千年",
               "守山谣",
               "永生之海",
               "有龙则灵"
               ]
    # dr.get_region_group(regions)
    dr.quest_invite()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Missing config name")
    else:
        name = sys.argv[1]
        RunTaskTest(name)
