from functools import cached_property
from pathlib import Path
import re
import time
import cv2
import numpy as np
from ppocronnx.predict_system import TextSystem, BoxedResult
from typing import List, Tuple, Optional, Any, cast

from module.base.logger import logger
from module.base.utils import float2str, merge_area

text_sys = TextSystem()

class RuleOcr:
    roi: tuple = ()
    area: tuple = ()
    keyword: str = ""
    score: float = 0.8  # 阈值默认为0.5

    def __init__(self, name: str, roi: tuple, area: tuple, keyword: str) -> None:
        self.name = name.upper()
        self.roi = roi
        self.area = area
        self.keyword = keyword

    @cached_property
    def name(self) -> str:
        """

        :return: The name of the OCR rule in uppercase
        """
        return self.name.upper()

    @cached_property
    def model(self) -> TextSystem:
        """Get the OCR text system model instance

        :return: TextSystem instance for OCR processing
        """
        return text_sys

    def coord(self) -> tuple:
        """
        获取坐标, 从roi随机获取坐标
        :return:
        """
        x, y, w, h = self.roi
        x += np.random.randint(0, w)
        y += np.random.randint(0, h)
        return x, y

    def crop(self, screenshot) -> np.ndarray:
        """
        截取图片
        """
        x, y, w, h = self.area
        return screenshot[y: y + h, x: x + w]

    def ocr_full(self, screenshot, keyword: Optional[str] = None) -> Tuple[int, int, int, int]:
        """
        检测整个图片的文本,并对结果进行过滤。返回的是匹配到的keyword的左边。如果没有匹配到返回(0, 0, 0, 0)
        :param screenshot: 要检测的图片
        :param keyword: 要匹配的关键词，如果为None则使用self.keyword
        :return: 匹配到的区域坐标 (x, y, width, height)
        """
        if keyword is None:
            keyword = self.keyword

        boxed_results = self.detect_and_ocr(screenshot)
        if not boxed_results:
            return 0, 0, 0, 0

        logger.background(f"<OCR> boxed_results: {boxed_results}")
        index_list = self.filter(boxed_results, keyword)
        logger.background(
            f"<OCR> [{keyword}] detected in {index_list} with {boxed_results[index_list[0]]}")
        # 如果一个都没有匹配到
        if not index_list:
            return 0, 0, 0, 0

        logger.background(f"<OCR> index_list: {index_list}")
        # 如果匹配到了多个,则合并所有的坐标，返回合并后的坐标
        if len(index_list) > 1:
            logger.info(f"<OCR> Going to merge areas.")
            area_list = [(
                int(cast(np.ndarray, boxed_results[index].box)[0][0]),  # x
                int(cast(np.ndarray, boxed_results[index].box)[0][1]),  # y
                int(cast(np.ndarray, boxed_results[index].box)[
                    # width
                    1][0] - cast(np.ndarray, boxed_results[index].box)[0][0]),
                int(cast(np.ndarray, boxed_results[index].box)[
                    # height
                    2][1] - cast(np.ndarray, boxed_results[index].box)[0][1]),
            ) for index in index_list]
            area = merge_area(area_list)
            self.roi = area[0] + self.roi[0], area[1] + \
                self.roi[1], self.roi[2], self.roi[3]
            self.area = area[0] + self.roi[0], area[1] + \
                self.roi[1], self.area[2], self.area[3]
        else:
            logger.info(f"<OCR> Found single area.")
            box = cast(np.ndarray, boxed_results[index_list[0]].box)
            self.roi = int(box[0][0] + self.roi[0]), int(box[0][1] + self.roi[1]
                                                         ), self.roi[2], self.roi[3]
            self.area = int(box[0][0] + self.roi[0]), int(box[0][1] + self.roi[1]
                                                          ), self.area[2], self.area[3]
        logger.background(
            f"<OCR> [{keyword if keyword else self.name}] detected in {self.area}, roi: {self.roi}")
        return self.area

    def ocr_single(self, screenshot) -> str:
        screenshot = self.crop(screenshot)
        res = text_sys.ocr_single_line(screenshot)
        if res is None:
            logger.warning(f"<ocr> No result found")
            return ""
        logger.info(f"<ocr> result: {res[0]}")
        return res[0]

    def digit_counter(self, screenshot) -> list:
        result = self.ocr_single(screenshot)
        if result == "":
            return [0, 0]

        result = re.search(r'(\d+)/(\d+)', result)
        if result:
            result = [int(s) for s in result.groups()]
            logger.info(f"ticket ocr result: {result}")
            count, total = result[0], result[1]
            if count > total:
                logger.critical(
                    f"realm raid ticket overflow!! Must be something wrong with OCR.")
            return result
        else:
            logger.warning(f'Unexpected ocr result: {result}')
            return [0, 0]

    def digit(self, image) -> int:
        """
        返回数字
        :param image:
        :return:
        """
        result = self.ocr_single(image)
        result = ''.join(re.findall(r'\d+', result))

        if result == "":
            return 0
        else:
            return int(result)

    def enlarge_canvas(self, image):
        """
        copy from https://github.com/LmeSzinc/StarRailCopilot
        Enlarge image into a square fill with black background. In the structure of PaddleOCR,
        image with w:h=1:1 is the best while 3:1 rectangles takes three times as long.
        Also enlarge into the integer multiple of 32 cause PaddleOCR will downscale images to 1/32.
        """
        height, width = image.shape[:2]
        length = int(max(width, height) // 32 * 32 + 32)
        border = (0, length - height, 0, length - width)
        if sum(border) > 0:
            image = cv2.copyMakeBorder(
                image, *border, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
        return image

    def detect_and_ocr(self, image) -> list[BoxedResult]:
        """
        注意：这里使用了预处理和后处理
        :param image:
        :return:
        """
        # pre process
        start_time = time.time()
        image = self.crop(image)
        image = self.enlarge_canvas(image)

        # ocr
        boxed_results: list[BoxedResult] = self.model.detect_and_ocr(image)
        results = []
        # after proces
        for result in boxed_results:
            # logger.background("ocr result score: %s" % result.score)
            if result.score < self.score:
                continue
            results.append(result)

        text_results = [result.ocr_text for result in results]
        logger.background(f"<OCR> detect results: {str(text_results)}")
        return results

    def filter(self, boxed_results: List[BoxedResult], keyword: Optional[str] = None) -> List[int]:
        """
        使用ocr获取结果后和keyword进行匹配. 返回匹配的index list
        :param boxed_results: OCR结果列表
        :param keyword: 要匹配的关键词，如果为None则使用self.keyword
        :return: 匹配到的索引列表
        """
        strings = [boxed_result.ocr_text for boxed_result in boxed_results]
        concatenated_string = "".join(strings)
        if keyword is None:
            keyword = self.keyword
        if keyword in concatenated_string:
            return [index for index, word in enumerate(strings) if keyword in word]
        return []
