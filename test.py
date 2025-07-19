import sys
from module.control.server.device import Device
from tasks.exploration.task_script import TaskScript as EXP
from tasks.royal_battle.task_script import TaskScript as RB
from module.base.logger import logger


def RunTaskTest(name):
    d = Device(config_name=name)
    exp = EXP(device=d)
    exp.add_backup_shiki()
    # r = RB(device=d)
    # r.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Missing config name")
    else:
        name = sys.argv[1]
        RunTaskTest(name)
