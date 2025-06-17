from typing import Optional
from ppadb.client import Client as AdbClient
import numpy as np
import cv2
import os

from module.base.logger import GameConsoleLogger

logger = GameConsoleLogger(debug_mode=True)

class ADBDevice:
    """ADBDevice class for Android device communication."""

    host = "127.0.0.1"
    port = 16384
    adb: AdbClient
    device = None
    screenshot = None

    def __init__(self, serial: str):
        """Initialize the ADBDevice."""
        self.port: Optional[int] = None
        self._split_serial(serial)
        self.device = self.connect_device()

    def _split_serial(self, serial: str):
        """Split the serial number into host and port."""
        serial_split = serial.split(":")
        self.host = serial_split[0].strip()
        self.port = int(serial_split[1].strip())

    def connect_device(self):
        """Connect to the device."""
        try:
            self.adb = AdbClient(host=self.host, port=5037)
            if self.port is not None:
                for i in range(3):
                    if self.adb.remote_connect(self.host, self.port + i):
                        logger.info(
                            f"connected to {self.host}:{self.port + i}")
                        self.port = self.port + i
                        self.device = self.adb.device(
                            f"{self.host}:{self.port + i}")
                        break
            else:
                logger.error("Port is None - cannot connect to device")

        except Exception as e:
            logger.error(f"Failed to connect to the device: {e}")
            return None
        return self.device

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
        if self.device is None:
            logger.error("Error: no device detected")
            return
        image = self.device.screencap()
        image = self.decode_image(image)
        self.screenshot = image
        return image

    def capture_screenshot(self, filepath):
        """Capture the screenshot."""
        image = self.get_screenshot()
        if image is None:
            logger.error("no image captured.")
            return
        cv2.imwrite(filepath, image)
        logger.info(f"got a screenshot in {filepath}")

    def click(self, x, y):
        """Click the screen."""
        if self.device is None:
            logger.error("Cannot click - no device connected")
            return
        logger.info(f"[Device] Click {x} {y}.")
        self.device.shell("input tap {} {}".format(x, y))

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
        self.click(x, y)

    def swipe(self, start_x, start_y, end_x, end_y, duration=300):
        """Swipe the screen."""
        if self.device is None:
            logger.error("Cannot swipe - no device connected")
            return
        logger.info(
            f"[Device] Swipe from ({start_x},{start_y}) to ({end_x},{end_y}) in {duration}.")
        self.device.shell("input swipe {} {} {} {} {}".format(
            start_x,
            start_y,
            end_x,
            end_y,
            duration
        ))
