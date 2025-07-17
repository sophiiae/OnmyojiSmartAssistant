from module.control.config.config import Config
from module.control.server.device import Device
from module.base.logger import logger
from tasks.shikigami_activity.task_script import TaskScript
import sys

if __name__ == "__main__":

    if len(sys.argv) < 2:
        logger.error("Missing config name")
    else:
        name = sys.argv[1]
        d = Device(config_name=name)
        task = TaskScript(d)
        logger.warning(
            f"Running Shikigami Activity for {d.config.config_name}")
        task.run()
