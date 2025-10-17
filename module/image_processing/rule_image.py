from functools import cached_property
from pathlib import Path
from random import Random
import cv2
import numpy as np
from typing import Optional

from module.base.logger import logger

class RuleImage:
    def __init__(self, name: str, roi: tuple, area: tuple, file: str) -> None:
        """
        初始化
        :param roi: roi
        :param area: 用于匹配的区域
        :param threshold: 阈值  0.8
        :param file: 相对路径, 带后缀
        """
        self._match_init = False  # 这个是给后面的 等待图片稳定
        self._image: Optional[np.ndarray] = None  # 这个是匹配的目标

        self.name = name.upper()
        self.roi: list = list(roi)
        self.area = area
        self.file = file

    def crop(self, screenshot) -> np.ndarray:
        """
        截取图片
        """
        x, y, w, h = int(self.area[0]), int(
            self.area[1]), int(self.area[2]), int(self.area[3])

        # Add bounds checking and validation
        if h <= 0 or w <= 0:
            logger.warning(
                f"[Image] {self.name} Invalid area dimensions: {self.area} (w={w}, h={h})")
            # Return whole screenshot
            return screenshot

        return screenshot[y: y + h, x: x + w]

    def coord(self) -> tuple:
        """
        获取坐标, 从roi随机获取坐标
        :return:
        """
        x, y, w, h = self.roi
        x += np.random.randint(0, w)
        y += np.random.randint(0, h)
        return x, y

    def set_area(self, x, y, w, h):
        self.area = (x, y, w, h)

    @property
    def image(self):
        """
        获取图片
        :return:
        """
        if self._image is None:
            self.load_image()
        return self._image

    def load_image(self) -> None:
        """
        加载图片
        :return:
        """
        if self._image is not None:
            return

        image = cv2.imread(self.file)
        self._image = image

    def roi_center(self) -> tuple:
        """
        获取roi的中心坐标
        :return:
        """
        x, y, w, h = self.roi
        return int(x + w // 2), int(y + h // 2)

    def roi_center_random(self) -> tuple:
        """
        获取roi的中心坐标
        :return:
        """
        x, y, w, h = self.roi
        c_x, c_y = int(x + w // 2), int(y + h // 2)
        offset_x = np.random.randint(0 - w // 2, w // 2)
        offset_y = np.random.randint(0 - h // 2, h // 2)
        return c_x + offset_x, c_y + offset_y

    def get_target_size(self):
        """
        获取目标大小
        """
        x, y, w, h = self.roi
        return {'w': w, 'h': h}

    def match_target(self, screenshot, threshold=0.9, debug=False, cropped=False) -> bool:
        if not cropped:
            screenshot = self.crop(screenshot)
        target = self.image
        if target is None:
            logger.error(f"[Image] {self.name} failed to load target image")
            return False

        # Check if template is larger than screenshot
        if target.shape[0] > screenshot.shape[0] or target.shape[1] > screenshot.shape[1]:
            logger.warning(
                f"[Image] {self.name} template size ({target.shape[1]}x{target.shape[0]}) is larger than screenshot size ({screenshot.shape[1]}x{screenshot.shape[0]}), skipping match")
            return False

        result = cv2.matchTemplate(screenshot, target, cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        logger.background(f"[Image] {self.name} match rate: {max_val}")

        if max_val >= threshold:
            self.roi[0] = max_loc[0] + self.area[0]
            self.roi[1] = max_loc[1] + self.area[1]
            logger.background(f"[Image] {self.name} updated roi: {self.roi}")
            if debug:
                self.draw_and_save(screenshot)
            return True
        return False

    def draw_and_save(self, screenshot):
        """For test ONLY

        Args:
            screenshot (np.array):
        """
        x, y, w, h = self.roi
        ax, ay, aw, ah = self.area
        target_rectangle_color = (101, 67, 196)
        area_rectangle_color = (56, 176, 0)
        cv2.rectangle(screenshot, (x, y), (x + w, y + h),
                      target_rectangle_color, 2)
        cv2.rectangle(screenshot, (ax, ay), (ax + aw, ay + ah),
                      area_rectangle_color, 2)

        path = f"{Path.cwd()}/{self.name}_output.png"
        logger.background(f"[Image] Save output with rectangle in {path}")
        cv2.imwrite(path, screenshot)
