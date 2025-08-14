from module.base.logger import logger

class DeviceNotRunningError(Exception):
    def __init__(self, msg="DeviceNotRunningError"):
        logger.error(msg)
        exit()
class GamePageUnknownError(Exception):
    def __init__(self):
        exit()

class RequestHumanTakeover(Exception):
    # Request human takeover
    # Alas is unable to handle such error, probably because of wrong settings.

    def __init__(self, msg="RequestHumanTakeover"):
        logger.critical(msg)
        exit()

class TaskEnd(Exception):
    def __init__(self, task="Name", msg=''):
        logger.warning(f"{task} ended. {msg}")

class ScriptError(Exception):
    # This is likely to be a mistake of developers, but sometimes a random issue
    def __init__(self, msg="ScriptError"):
        logger.error(msg)
        exit()

class GameStuckError(Exception):
    def __init__(self, msg="GameStuckError"):
        logger.error(msg)
        exit()

class GameNotRunningError(Exception):
    def __init__(self, msg="GameNotRunningError"):
        logger.error(msg)
        exit()

class GameTooManyClickError(Exception):
    def __init__(self, msg="GameTooManyClickError"):
        logger.error(msg)
        exit()
