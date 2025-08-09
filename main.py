from module.base.logger import logger
from tasks.duel.task_script import TaskScript as RB
from tasks.exploration.task_script import TaskScript as EXP
from module.script import Script
from module.control.server.device import Device
import sys
import os

# 设置工作目录
def setup_working_directory():
    """设置正确的工作目录"""
    if getattr(sys, 'frozen', False):
        # 如果是exe环境，使用exe所在目录
        base_path = os.path.dirname(sys.executable)
    else:
        # 如果是开发环境，使用当前目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    os.chdir(base_path)
    return base_path


# 设置工作目录
setup_working_directory()


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
