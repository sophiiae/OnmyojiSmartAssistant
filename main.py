import sys
from module.control.server.device import Device
from module.script import Script
from tasks.exploration.task_script import TaskScript as EXP
from tasks.royal_battle.task_script import TaskScript as RB

from module.base.logger import logger

# port = 16384  # 浅 default
# port = 16416  # 念
# port = 16448  # 小
# port = 16480  # 3
# port = 16512  # 4
# port = 16544  # 5

def RunScript(config_name: str):
    logger.info(f"Start running script: {config_name}")

    script = Script(config_name)
    script.start()

def RunTaskTest(name):
    d = Device(config_name=name)
    t = EXP(device=d)
    t.run()
    r = RB(device=d)
    r.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Missing config name")
    else:
        name = sys.argv[1]
        RunScript(name)
        # RunTaskTest(name)
