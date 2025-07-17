from functools import cached_property
import os
import subprocess
import time
import psutil
import pyautogui
import cv2

from module.base.exception import DeviceNotRunningError, RequestHumanTakeover
from module.control.config.config import Config
from module.image_processing.image_processor import ImageProcessor
from module.base.logger import GameConsoleLogger
from module.control.server.device import Device

mumu_path = r"C:\Program Files\Netease\MuMu Player 12\shell\MuMuPlayer.exe"
mumu_multi_player_path = r"C:\Program Files\Netease\MuMu Player 12\shell\MuMuMultiPlayer.exe"

logger = GameConsoleLogger(debug_mode=False)

class EmulatorMain:
    delay_between_instances = 15  # 实例启动间隔（秒）
    max_retries = 2               # 失败重试次数
    mumu_path = mumu_path  # MuMu模拟器路径
    mumu_multi_player_path = mumu_multi_player_path  # MuMu多开器路径

    def __init__(self, config_name: str):
        self.name = config_name

    def start_mumu12(self):
        # 检查MuMu12是否已经运行
        try:
            # 使用tasklist命令检查MuMu12进程
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq MuMuPlayer.exe'],
                                    capture_output=True, text=True)
            if 'MuMuPlayer.exe' in result.stdout:
                logger.background("MuMu12模拟器已经在运行中。")
                return True
        except Exception as e:
            logger.error(f"检查MuMu12进程时出错: {e}")
            return False

        if not os.path.exists(self.mumu_path):
            logger.error(f"未找到MuMu12模拟器，请确认安装路径是否正确: {self.mumu_path}")
            return False

        # 启动MuMu12模拟器
        try:
            logger.background("正在启动MuMu12模拟器...")
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
                logger.background("MuMu12模拟器已经在运行中。")
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
            logger.background("正在启动MuMu12多开器...")
            subprocess.Popen([self.mumu_multi_player_path])
            while 1:
                time.sleep(2)  # 等待多开器启动
                # 检查MuMu12多开器是否启动成功
                if self.check_mumu_process():
                    logger.success("MuMu12多开器已启动成功！")
                    break
                else:
                    logger.background("等待MuMu12多开器启动...")
            return True
        except Exception as e:
            logger.error(f"启动MuMu12多开器时出错: {e}")
            return False

    def activate_all_mumu(self) -> bool:
        if not self.start_mumu_multi():  # 启动MuMu多开器
            return False

        logger.background("正在激活所有MuMu模拟器...")
        while 1:
            time.sleep(2)  # 等待多开器启动
            # 检查MuMu12多开器是否启动成功
            if self.check_mumu_process():
                logger.success("MuMu12多开器已启动成功！")
                break
            else:
                logger.background("等待MuMu12多开器启动...")

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
        logger.background("所有MuMu模拟器已激活！")
        return True

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
                logger.background(
                    f"已终止进程: {proc.info['name']} (PID: {proc.pid})")

    def start_onmyoji(self, device: Device):
        logger.background(f" 🎮 启动阴阳师 {device.port}...")

        self.check_ad(device)
        self.click_onmyoji(device)
        time.sleep(0.5)
        self.login(device)

    def click_onmyoji(self, device: Device):
        # device.capture_screenshot(f"{device.port}.png")
        screenshot = device.get_screenshot()
        pro = ImageProcessor(screenshot)

        center = pro.get_match_center(self.get_image_path('logo.png'))
        if center is not None:
            device.click(center[0], center[1])
            logger.success(f"找到阴阳师Logo，正在启动...")
        else:
            logger.error("未找到阴阳师Logo, 请检查图片路径和截图质量！")
            raise DeviceNotRunningError("未找到阴阳师Logo, 请检查图片路径和截图质量！")

    def check_ad(self, device: Device):
        screenshot = device.get_screenshot()
        pro = ImageProcessor(screenshot)
        center = pro.get_match_center(self.get_image_path('ad_close_icon.png'))
        if center is not None:
            logger.success(f"找到广告关闭按钮，正在关闭...")
            device.click(center[0], center[1])
            time.sleep(0.5)
        else:
            logger.background("没有发现广告")

    def login(self, device: Device):
        screenshot = device.get_screenshot()
        pro = ImageProcessor(screenshot)
        image = cv2.imread(self.get_image_path('login_warning.png'))
        result = pro.find_target(image)
        if result:
            device.click(600, 600)


if __name__ == "__main__":
    emulator = EmulatorMain(config_name="fairy")
