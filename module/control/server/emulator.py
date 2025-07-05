from module.control.config.config import Config
from module.base.logger import GameConsoleLogger
from module.control.server.device import Device
from module.control.server.emulator_main import EmulatorMain

logger = GameConsoleLogger(debug_mode=False)

class Emulator(EmulatorMain):
    main_device: Device

    def __init__(self, config_name: str):
        super().__init__(config_name)
        self.config = Config(config_name=self.name)

    def start_main_onmyoji(self):
        if self.start_mumu12():
            logger.success("MUMU12模拟器已启动！")
            self.main_device = Device(
                self.config.model.script.device.serial)
            self.start_onmyoji(self.main_device)
        else:
            logger.error("启动失败，请检查错误信息！")


if __name__ == "__main__":
    emulator = Emulator(config_name="fairy")
    emulator.start_main_onmyoji()
