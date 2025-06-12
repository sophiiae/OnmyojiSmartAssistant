import os
import subprocess
import sys
import time
import psutil
import pyautogui
import concurrent.futures

from module.base.exception import DeviceNotRunningError
from trifle_fairy.config.config import Config
from module.image_processing.image_processor import ImageProcessor
from module.base.logger import logger
from module.control.server.adb_device import ADBDevice

mumu_path = r"C:\Program Files\Netease\MuMu Player 12\shell\MuMuPlayer.exe"
mumu_multi_player_path = r"C:\Program Files\Netease\MuMu Player 12\shell\MuMuMultiPlayer.exe"

class Emulator:
    delay_between_instances = 15  # 实例启动间隔（秒）
    max_retries = 2               # 失败重试次数
    main_device = None
    sub_devices = []  # Initialize as empty list
    mumu_path = mumu_path  # MuMu模拟器路径
    mumu_multi_player_path = mumu_multi_player_path  # MuMu多开器路径

    def __init__(self, config: Config):
        self.config = config
        self.name = config.config_name

    def start_mumu12(self):
        # 检查MuMu12是否已经运行
        try:
            # 使用tasklist命令检查MuMu12进程
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq MuMuPlayer.exe'],
                                    capture_output=True, text=True)
            if 'MuMuPlayer.exe' in result.stdout:
                logger.info("MuMu12模拟器已经在运行中。")
                return True
        except Exception as e:
            logger.error(f"检查MuMu12进程时出错: {e}")
            return False

        if not os.path.exists(self.mumu_path):
            logger.error(f"未找到MuMu12模拟器，请确认安装路径是否正确: {self.mumu_path}")
            return False

        # 启动MuMu12模拟器
        try:
            logger.info("正在启动MuMu12模拟器...")
            subprocess.Popen([self.mumu_path])
            time.sleep(10)  # 等待模拟器启动完成
            return True
        except Exception as e:
            logger.error(f"启动MuMu12模拟器时出错: {e}")
            return False

    def check_mumu_process(self):
        """检查MuMu模拟器是否正在运行"""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in ['MuMuPlayer.exe', 'MuMuMultiPlayer.exe']:
                return True
        return False

    def start_mumu_multi(self):
        # 检查MuMu12是否已经运行
        try:
            # 使用tasklist命令检查MuMu12进程
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq MuMuPlayer.exe'],
                                    capture_output=True, text=True)
            if 'MuMuPlayer.exe' in result.stdout:
                logger.info("MuMu12模拟器已经在运行中。")
                return True
        except Exception as e:
            logger.error(f"检查MuMu12进程时出错: {e}")
            return False

        if not os.path.exists(self.mumu_multi_player_path):
            logger.error(
                f"未找到MuMu12多开器，请确认安装路径是否正确: {self.mumu_multi_player_path}")
            return False

        # 启动MuMu12多开器
        try:
            logger.info("正在启动MuMu12多开器...")
            subprocess.Popen([self.mumu_multi_player_path])
            while 1:
                time.sleep(2)  # 等待多开器启动
                # 检查MuMu12多开器是否启动成功
                if self.check_mumu_process():
                    logger.success("MuMu12多开器已启动成功！")
                    break
                else:
                    logger.info("等待MuMu12多开器启动...")
            return True
        except Exception as e:
            logger.error(f"启动MuMu12多开器时出错: {e}")
            return False

    def activate_all_mumu(self) -> bool:
        if not self.start_mumu_multi():  # 启动MuMu多开器
            return False

        logger.info("正在激活所有MuMu模拟器...")
        while 1:
            time.sleep(2)  # 等待多开器启动
            # 检查MuMu12多开器是否启动成功
            if self.check_mumu_process():
                logger.success("MuMu12多开器已启动成功！")
                break
            else:
                logger.info("等待MuMu12多开器启动...")

        try:
            select_all = pyautogui.locateOnScreen(
                self.get_image_path('select_all.png'), confidence=0.9, region=(1350, 750, 200, 70))
            if select_all is not None:
                logger.success("找到MuMu12多开器的全选栏，正在激活...")
                pyautogui.click(1395, 785)  # 点击全选栏位置
                time.sleep(1)
        except pyautogui.ImageNotFoundException:
            logger.error("未找到MuMu12多开器的全选栏，请检查图片路径和截图质量！")
            return False

        try:
            start_all = pyautogui.locateOnScreen(
                self.get_image_path('start_all.png'), confidence=0.9, region=(1350, 1450, 100, 100))
            if start_all is not None:
                logger.success("找到MuMu12多开器的全部开始按钮，正在点击...")
                pyautogui.click(start_all)
        except pyautogui.ImageNotFoundException:
            logger.error("未找到MuMu12多开器的开始按钮，请检查图片路径和截图质量！")
            return False

        time.sleep(30)  # 等待模拟器启动完成
        logger.info("所有MuMu模拟器已激活！")
        return True

    def multi_mumu_start_with_retry(self) -> list[ADBDevice]:
        logger.info("===== MuMu多开自动启动脚本 =====")
        # 尝试启动模拟器和游戏
        activated_devices = []
        for attempt in range(self.max_retries):
            logger.info(f"尝试第 {attempt + 1} 次启动...")
            is_started = self.check_mumu_process() or self.activate_all_mumu()
            if is_started:
                activated_devices = self.get_all_devices()
                if len(activated_devices) > 0:
                    break

            activated_devices = []
            self.kill_mumu_process()
            logger.warning("启动失败，正在重试...")
            time.sleep(self.delay_between_instances)  # 等待一段时间后重试

        if len(activated_devices) == 0:
            logger.error("所有启动方式均失败，请检查配置！")
            raise DeviceNotRunningError("所有启动方式均失败，请检查配置！")
        return activated_devices

    def get_all_devices(self):
        activated_devices = []
        success = True
        logger.info(f"正在获取所有设备...")
        hosts = [self.config.model.script.main_host] + \
            self.config.model.script.subhosts
        for host in hosts:
            d = ADBDevice(host)
            if d.device is None:
                success = False
                break
            activated_devices.append(d)
        return activated_devices if success else []

    def get_image_path(self, file_name: str) -> str:
        """获取图片文件的绝对路径"""
        current_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(current_dir, '../res/', file_name)

    def kill_mumu_process(self, multi_only: bool = False):
        """强制结束所有MuMu模拟器进程"""
        processes = ['MuMuMultiPlayer.exe']
        if not multi_only:
            processes.append('MuMuPlayer.exe')

        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in processes:
                proc.kill()
                logger.info(f"已终止进程: {proc.info['name']} (PID: {proc.pid})")

    def start_onmyoji(self, device: ADBDevice, is_main: bool = False):
        logger.info(f" 🎮 启动阴阳师 {device.port}...")

        self.check_ad(device)
        self.click_onmyoji(device, is_main)

    def click_onmyoji(self, device: ADBDevice, is_main: bool = False):
        device.capture_screenshot(f"{device.port}.png")
        screenshot = device.get_screenshot()
        pro = ImageProcessor(screenshot)

        logos = ['logo.png', 'logo_sub.png']
        for logo in logos:
            center = pro.get_match_center(self.get_image_path(logo))
            if center is not None:
                device.click(center[0], center[1])
                logger.success(f"找到阴阳师Logo，正在启动...")
                break
        else:
            logger.error("未找到阴阳师Logo, 请检查图片路径和截图质量！")
            raise DeviceNotRunningError("未找到阴阳师Logo, 请检查图片路径和截图质量！")

    def check_ad(self, device: ADBDevice):
        screenshot = device.get_screenshot()
        pro = ImageProcessor(screenshot)
        center = pro.get_match_center(self.get_image_path('ad_close_icon.png'))
        if center is not None:
            logger.success(f"找到广告关闭按钮，正在关闭...")
            device.click(center[0], center[1])
            time.sleep(0.5)
        else:
            logger.info("没有发现广告")

    def start_main_onmyoji(self):
        if self.start_mumu12():
            logger.success("MUMU12模拟器已启动！")
            self.main_device = ADBDevice(
                self.config.model.script.main_host)
            self.start_onmyoji(self.main_device, True)
        else:
            logger.error("启动失败，请检查错误信息！")

    def start_all_onmyoji(self):
        self.sub_devices = self.multi_mumu_start_with_retry()
        logger.success("MUMU所有模拟器已启动！")
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(self.start_onmyoji, self.sub_devices)
        # for device in self.sub_devices:
        #     self.start_onmyoji(device)


if __name__ == "__main__":
    emulator = Emulator(Config("fairy"))

    args = sys.argv
    if len(args) > 1 and sys.argv[1] == '-m':
        emulator.start_main_onmyoji()
    else:
        emulator.start_all_onmyoji()
