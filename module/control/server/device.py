from typing import Optional
from ppadb.client import Client as AdbClient
import numpy as np
import cv2
import subprocess
import time

from module.base.logger import logger, set_current_config_name
from module.config.config import Config
from module.base.timer import Timer
from collections import deque
from module.base.exception import DeviceNotRunningError, GameStuckError, GameTooManyClickError

class Device:
    """Device class for Android device communication."""

    host = "127.0.0.1"
    port = 16384
    adb: AdbClient
    device = None
    screenshot = None
    config: Config
    detect_record = set()
    click_record = deque(maxlen=15)
    stuck_timer = Timer(60, retry_max=60).start()
    stuck_timer_long = Timer(300, retry_max=300).start()
    stuck_long_wait_list = ['BATTLE_STATUS_S', 'PAUSE', 'LOGIN_CHECK']

    def __init__(self, config_name: str):
        """Initialize the Device."""
        self.port: Optional[int] = None
        self.config_name = config_name  # 保存配置名称
        self.config = Config(config_name=config_name)
        self._split_serial(self.config.model.script.device.serial)
        self.device = self.connect_device()

    def _split_serial(self, serial: str):
        """Split the serial number into host and port."""
        serial_split = serial.split(":")
        self.host = serial_split[0].strip()
        self.port = int(serial_split[1].strip())

    def _ensure_adb_server_running(self):
        """Ensure ADB server is running and accessible."""
        try:
            # First try to kill any existing ADB server
            logger.info("Try to kill any ADB server")
            subprocess.run(['adb', 'kill-server'],
                           capture_output=True, timeout=5)
            time.sleep(1)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("ADB command not found or timeout")
            return False

        try:
            # Start ADB server
            logger.info("Try to start ADB server")
            subprocess.run(['adb', 'start-server'],
                           capture_output=True, timeout=10)
            time.sleep(1)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("Failed to start ADB server")
            return False

    def _test_connection(self) -> bool:
        # Test connection
        try:
            self.adb.devices()
            logger.background("ADB server connection successful")
        except Exception as e:
            logger.error(f"Failed to connect to ADB server: {e}")
            # Ensure ADB server is running
            if not self._ensure_adb_server_running():
                logger.error("Failed to start ADB server")
            return False
        return True

    def connect_device(self):
        """Connect to the device."""
        try:
            # Try to connect to ADB server
            self.adb = AdbClient(host=self.host, port=5037)
            has_connection = False
            for _ in range(3):
                has_connection = self._test_connection()
                if has_connection:
                    break

            if has_connection and self.port is not None:
                for i in range(3):
                    if self.adb.remote_connect(self.host, self.port + i):
                        logger.background(
                            f"connected to {self.host}:{self.port + i}")
                        self.port = self.port + i
                        self.device = self.adb.device(
                            f"{self.host}:{self.port + i}")
                        break
            else:
                logger.error("Port is None - cannot connect to device")

        except Exception as e:
            logger.error(f"Failed to connect to the device: {e}")
            raise DeviceNotRunningError()
        return self.device

    def stuck_record_add(self, button):
        """
        当你要设置这个时候检测为长时间的时候，你需要在这里添加
        如果取消后，需要在`stuck_record_clear`中清除
        :param button:
        :return:
        """
        self.detect_record.add(str(button))
        logger.background(f'Add stuck record: {button}')

    def stuck_record_clear(self):
        self.detect_record = set()
        self.stuck_timer.reset()
        self.stuck_timer_long.reset()

    def stuck_record_check(self):
        """
        Raises:
            GameStuckError:
        """
        reached = self.stuck_timer.reached()
        reached_long = self.stuck_timer_long.reached()

        if not reached:
            return False
        if not reached_long:
            for button in self.stuck_long_wait_list:
                if button in self.detect_record:
                    return False

        logger.warning(f'Waiting for {self.detect_record}')
        self.stuck_record_clear()

        raise GameStuckError(f'Wait too long.')

    def handle_control_check(self, button):
        self.stuck_record_clear()
        self.click_record_add(button)
        self.click_record_check()

    def click_record_add(self, button):
        self.click_record.append(str(button))

    def click_record_clear(self):
        self.click_record.clear()

    def click_record_check(self):
        """
        Raises:
            GameTooManyClickError:
        """
        count = {}
        for key in self.click_record:
            count[key] = count.get(key, 0) + 1
        count = sorted(count.items(), key=lambda item: item[1])
        if count[0][1] >= 12:
            logger.warning(f'Too many click for a button: {count[0][0]}')
            logger.warning(f'History click: {
                           [str(prev) for prev in self.click_record]}')
            self.click_record_clear()
            raise GameTooManyClickError(
                f'Too many click for a button: {count[0][0]}')
        if len(count) >= 2 and count[0][1] >= 6 and count[1][1] >= 6:
            logger.warning(f'Too many click between 2 buttons: {
                           count[0][0]}, {count[1][0]}')
            logger.warning(f'History click: {
                           [str(prev) for prev in self.click_record]}')
            self.click_record_clear()
            raise GameTooManyClickError(f'Too many click between 2 buttons: {
                                        count[0][0]}, {count[1][0]}')

    def decode_image(self, image):
        """Decode the image."""
        image_bytes = np.array(image, dtype=np.uint8)
        image = cv2.imdecode(np.frombuffer(
            image_bytes, np.uint8), cv2.IMREAD_COLOR)
        return image

    def get_screenshot(self):
        """
        Returns:
            np.ndarray:
        """
        # 设置当前配置名称上下文，确保日志能正确关联
        set_current_config_name(self.config_name)

        if self.device is None:
            logger.error("Error: no device detected")
            return
        image = self.device.screencap()
        image = self.decode_image(image)
        self.screenshot = image
        return image

    def capture_screenshot(self, filepath) -> bool:
        """Capture the screenshot."""
        # 设置当前配置名称上下文，确保日志能正确关联
        set_current_config_name(self.config_name)

        image = self.get_screenshot()
        if image is None:
            logger.error("模拟器截图失败.")
            return False
        cv2.imwrite(filepath, image)
        logger.info(f"图像已保存: {filepath}")
        return True

    def click(self, x, y, name: str):
        """Click the screen."""
        # 设置当前配置名称上下文
        set_current_config_name(self.config_name)

        if self.device is None:
            logger.error("Cannot click - no device connected")
            return
        logger.background(f"[Device] Click {name}: {x} {y}.")
        self.device.shell("input tap {} {}".format(x, y))

    def long_click(self, x: float, y: float, duration: float = 1500):
        if self.device is None:
            logger.error("Cannot click - no device connected")
            return

        logger.background(
            f"[Device] Long Click {x} {y} in {duration}.")

        self.device.shell(
            "input swipe {} {} {} {} {}".format(x, y, x, y, duration))

    def random_click(self, x, y, w, h):
        """Random click within a rectangle."""
        if self.device is None:
            logger.error("Cannot click - no device connected")
            return
        if (x < 0 or y < 0 or x + w > 1280 or y + h > 720):
            logger.error("Invalid rectangle.")
            return
        x = np.random.randint(x, x + w)
        y = np.random.randint(y, y + h)
        self.click(x, y, "Random right")

    def swipe(self, start_x, start_y, end_x, end_y, duration=300):
        """Swipe the screen."""
        if self.device is None:
            logger.error("Cannot swipe - no device connected")
            return
        logger.background(
            f"[Device] Swipe from ({start_x},{start_y}) to ({end_x},{end_y}) in {duration}.")
        self.device.shell("input swipe {} {} {} {} {}".format(
            start_x,
            start_y,
            end_x,
            end_y,
            duration
        ))


if __name__ == "__main__":
    device = Device(config_name='osa')
    device.capture_screenshot("screenshot.png")
