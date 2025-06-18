import sys
import time
import concurrent.futures

from module.base.exception import DeviceNotRunningError
from module.base.logger import GameConsoleLogger
from module.control.server.adb_device import ADBDevice
from module.control.server.emulator_main import EmulatorMain
from trifle_fairy.config.config import Config

logger = GameConsoleLogger(debug_mode=False)

class Emulator(EmulatorMain):
    main_device: ADBDevice
    sub_devices: list[ADBDevice]

    def __init__(self, config_name: str):
        super().__init__(config_name)
        self.config = Config()

    def multi_mumu_start_with_retry(self) -> list[ADBDevice]:
        logger.info("===== MuMu多开自动启动脚本 =====")
        # 尝试启动模拟器和游戏
        activated_devices = []
        for attempt in range(self.max_retries):
            logger.info(f"尝试第 {attempt + 1} 次启动...")
            is_started = self.check_mumu_process() or self.activate_all_mumu()
            if is_started:
                logger.info("正在获取所有设备...")
                for attempt in range(self.max_retries):
                    logger.info(f"尝试第 {attempt + 1} 次获取设备...")
                    hosts = [self.config.model.script.main_host] + \
                        self.config.model.script.subhosts
                    activated_devices = self.get_all_devices(hosts)
                    if len(activated_devices) == len(self.config.model.script.subhosts) + 1:
                        return activated_devices
                    else:
                        logger.info("设备数量不匹配，正在重试...")
                        time.sleep(self.delay_between_instances)

            activated_devices = []
            self.kill_mumu_process()
            logger.warning("启动失败，正在重试...")
            time.sleep(self.delay_between_instances)  # 等待一段时间后重试

        if len(activated_devices) == 0:
            logger.error("所有启动方式均失败，请检查配置！")
            raise DeviceNotRunningError("所有启动方式均失败，请检查配置！")
        return activated_devices

    def get_all_devices(self, hosts):
        activated_devices = []
        success = True
        logger.info(f"正在获取所有设备...")

        for host in hosts:
            d = ADBDevice(host)
            if d.device is None:
                success = False
                break
            activated_devices.append(d)
            time.sleep(2)
        return activated_devices if success else []

    def get_main_device(self):
        self.main_device = ADBDevice(
            self.config.model.script.main_host)

    def get_all_sub_devices(self):
        self.sub_devices = self.get_all_devices(
            self.config.model.script.subhosts)

    def start_main_onmyoji(self):
        if self.start_mumu12():
            logger.success("MUMU12模拟器已启动！")
            self.get_main_device()
            self.start_onmyoji(self.main_device)
            time.sleep(0.5)
            self.login(self.main_device)
        else:
            logger.error("启动失败，请检查错误信息！")

    def start_all_onmyoji(self):
        self.sub_devices = self.multi_mumu_start_with_retry()
        self.kill_mumu_process(multi_only=True)
        logger.success("MUMU所有模拟器已启动！")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(self.start_onmyoji, self.sub_devices)

        time.sleep(1)
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(self.login, self.sub_devices)


if __name__ == "__main__":
    emulator = Emulator(config_name="fairy")

    args = sys.argv
    if len(args) > 1 and sys.argv[1] == '-m':
        emulator.start_main_onmyoji()
    else:
        emulator.start_all_onmyoji()
