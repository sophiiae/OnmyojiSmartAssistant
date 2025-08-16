from module.base.logger import logger

class DeviceNotRunningError(Exception):
    def __init__(self, msg="DeviceNotRunningError"):
        logger.error(msg)
        super().__init__(msg)
class GamePageUnknownError(Exception):
    def __init__(self, msg=''):
        logger.critical(msg)
        super().__init__(msg)

class RequestHumanTakeover(Exception):
    # Request human takeover
    # Alas is unable to handle such error, probably because of wrong settings.

    def __init__(self, msg="RequestHumanTakeover"):
        logger.critical(msg)
        super().__init__(msg)

class TaskEnd(Exception):
    def __init__(self, task="Name", msg=''):
        logger.warning(f"{task} ended. {msg}")
        super().__init__(msg)

class ScriptError(Exception):
    # This is likely to be a mistake of developers, but sometimes a random issue
    def __init__(self, msg="ScriptError"):
        logger.error(msg)
        super().__init__(msg)

class GameStuckError(Exception):
    def __init__(self, msg="GameStuckError"):
        logger.error(msg)
        super().__init__(msg)

class GameNotRunningError(Exception):
    def __init__(self, msg="GameNotRunningError"):
        logger.error(msg)
        super().__init__(msg)

class GameTooManyClickError(Exception):
    def __init__(self, msg="GameTooManyClickError"):
        logger.error(msg)
        super().__init__(msg)
