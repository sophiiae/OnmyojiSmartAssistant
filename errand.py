import sys
import time
from module.control.server.device import Device
from module.base.logger import logger
from tasks.general.summon import Summon
from tasks.realm_raid.guild_raid import GuildRaid
from tasks.main_page.colla import Colla
from tasks.realm_raid.task_script import TaskScript as RR
from tasks.minamoto.task_script import TaskScript as MINAMOTO
from tasks.task_base import TaskBase
from tasks.main_page.routine import Routine
from tasks.goryou_realm.task_script import TaskScript as YL
from tasks.regional_boss.task_script import TaskScript as Boss

def RunBoss(config_name: str):
    d = Device(config_name)
    b = Boss(device=d)
    b.run()


def RunYuLing(config_name: str):
    d = Device(config_name)
    s = YL(device=d)
    s.run()

def RunRegularSummon(config_name: str):
    logger.info(f"Start running regualr summon for script: {config_name}")

    d = Device(config_name)
    s = Summon(device=d)
    s.run()

def RunGuildRaid(config_name: str):
    logger.info(f"Start running regualr summon for script: {config_name}")

    d = Device(config_name)
    g = GuildRaid(device=d)
    g.start_guild_raid()

def RunColla(config_name: str):
    logger.info(f"Start running regualr summon for script: {config_name}")

    d = Device(config_name)
    colla = Colla(device=d)
    colla.start_colla()

def RunDailyRountine(name, colla: bool = True):
    d = Device(config_name=name)
    r = Routine(device=d)
    # r.run()
    r.run_single_account(colla)
    # r.get_store_gift()
    # r.get_huahe()

def RunRealmRaid(config_name: str):
    logger.info(f"Start running 3 win realm raid for script: {config_name}")

    d = Device(config_name)
    rr = RR(device=d)
    rr.run()

def RunMinamoto(config_name: str):
    logger.info(f"Start running minamoto for script: {config_name}")

    d = Device(config_name)
    minamoto = MINAMOTO(device=d)
    minamoto.run()
    # minamoto.goto(page_minamoto)
    # minamoto.goto(page_main, page_minamoto)

def WaitingMode(name: str):
    d = Device(config_name=name)
    b = TaskBase(device=d)
    count = 0
    while count < 3:
        time.sleep(1)
        if b.wait_request():
            count += 1


# py ./errand.py [script_name] -g
if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.warning("Args[0]: config name")
        logger.warning(
            "Args[1]: -g: run guild raid | -r: run 3 win realm raid")
        logger.warning(
            "Agrs[1]: -s: run regular summon | -c: run daily collaboration")
        logger.warning(
            "Agrs[1]: -m: run minamoto | -w: waiting mode | -d: daily routine(colla)")
    else:
        name, t = sys.argv[1:]
        match t:
            case '-g':
                RunGuildRaid(name)
            case '-s':
                RunRegularSummon(name)
            case '-c':
                RunColla(name)
            case '-r':
                RunRealmRaid(name)
            case '-m':
                RunMinamoto(name)
            case '-w':
                WaitingMode(name)
            case '-d':
                RunDailyRountine(name, False)
            case '-dc':
                RunDailyRountine(name)
            case '-yl':
                RunYuLing(name)
            case '-b':
                RunBoss(name)
            case _:
                logger.warning(
                    "Missing args, try 'py ./errand.py' for instruction")
