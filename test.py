import sys
from module.control.server.device import Device
from tasks.daily_routine.task_script import TaskScript as TS
from tasks.duel.task_script import TaskScript as RB
from module.base.logger import logger


def RunTaskTest(name):
    d = Device(config_name=name)
    dr = TS(device=d)
    dr.get_store_gift()
    # exp.soul_clear(exp.I_EXP_C_CHAPTER)
    # r = RB(device=d)
    # r.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Missing config name")
    else:
        name = sys.argv[1]
        RunTaskTest(name)
