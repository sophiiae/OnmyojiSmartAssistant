import json
import os
from pathlib import Path
import sys
import cv2
from cv2.typing import MatLike
import numpy as np
from typing import Optional, Tuple
from module.base.logger import logger

class ImageProcessor:
    screenshot: Optional[MatLike] = None
    target_rectangle_color = (101, 67, 196)
    area_rectangle_color = (56, 176, 0)

    def __init__(self, screenshot) -> None:
        self.screenshot = screenshot

    def parse_dir(self, dir: str, draw_output: bool = False):
        res = []
        for file in os.listdir(dir):
            if (file.endswith('.png')):
                name = file.split('.')[0]
                logger.background(f"*** start processing file: {file}")

                image = cv2.imread(f"{dir}/{file}")
                roi = self.find_target(image)
                if roi is not None:
                    area = self.get_area(roi)
                    res.append({
                        'name': name,
                        'roi': f"{roi[0]}, {roi[1]}, {roi[2]}, {roi[3]}",
                        'area': f"{area[0]}, {area[1]}, {area[2]}, {area[3]}",
                        'file': f"{dir}/{file}",
                        'description': ''
                    })
                else:
                    logger.error(f"Error: no target found for {file}")
        if draw_output:
            for item in res:
                roi = item['roi'].split(',')
                area = item['area'].split(',')

                self.draw_rectange(
                    (roi[0], roi[1]), (roi[0] + roi[2], roi[1] + roi[3]),
                    self.target_rectangle_color
                )
                self.draw_rectange(
                    (area[0], area[1]), (area[0] + area[2], area[1] + area[3]),
                    self.area_rectangle_color
                )
        return res

    def parse_image_file(self, path):
        image = cv2.imread(path)
        logger.background(f"path: {path}")
        return self.start_process(path, image=image)

    def start_process(self, path, image):
        logger.background(f"**** start processing image ****")
        roi = self.find_target(image)
        if roi is not None:
            area = self.get_area(roi)

            logger.background("Drawing target and area rectangles...")
            self.draw_rectange(
                (roi[0], roi[1]), (roi[0] + roi[2], roi[1] + roi[3]), self.target_rectangle_color)
            self.draw_rectange(
                (area[0], area[1]), (area[0] + area[2], area[1] + area[3]), self.area_rectangle_color)

            name = self.get_name_from_path(path)
            path = path.replace('\\', '/')
            return {
                'name': f"{name}",
                'type': "image",
                'roi': f"{roi[0]}, {roi[1]}, {roi[2]}, {roi[3]}",
                'area': f"{area[0]}, {area[1]}, {area[2]}, {area[3]}",
                'file': f"{path}",
                'description': ''
            }
        else:
            logger.error("Error: no target found.")

    def get_match_center(self, path) -> Optional[Tuple[int, int]]:
        image = cv2.imread(path)
        result = self.find_target(image)
        if result is not None:
            x, y, w, h = result
            center_x = int(x) + (int(w) // 2)
            center_y = int(y) + (int(h) // 2)
            return center_x, center_y
        return None

    def get_name_from_path(self, path: str):
        file = path.split('\\')[-1]
        return file.split('.')[0]

    def match_all_target(self, path):
        image = cv2.imread(path)
        print(f"path: {path}")
        if self.screenshot is None or image is None:
            return None
        # 目標取樣
        result = cv2.matchTemplate(
            self.screenshot, image, cv2.TM_CCORR_NORMED
        )
        return result

    def find_target(self, target: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        # 目標取樣
        if self.screenshot is None:
            return None
        result = cv2.matchTemplate(
            self.screenshot, target, cv2.TM_CCORR_NORMED
        )
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.95:
            logger.background(f"match rate: {max_val}")
            x, y = max_loc
            h, w, c = target.shape
            return (x, y, w, h)
        return None

    def calculated(self, result, shape):
        """暂时不用
        """
        mat_top, mat_left = result['max_loc']
        target_h, target_w, target_channels = shape

        x = {
            'left': int(mat_top),
            'center': int((mat_top + mat_top + target_w) / 2),
            'right': int(mat_top + target_w),
        }

        y = {
            'top': int(mat_left),
            'center': int((mat_left + mat_left + target_h) / 2),
            'bottom': int(mat_left + target_h),
        }

        return {'x': x, 'y': y}

    def draw_rectange(self, top_left: Tuple[int, int], bottom_right: Tuple[int, int], color: Tuple[int, int, int]) -> None:
        if self.screenshot is None:
            return
        cv2.rectangle(self.screenshot, top_left, bottom_right, color, 2)

    def get_area(self, roi):
        """Draw a area for detecting target instead of full screenshot
           划定一个区域用来识别目标，减少识别耗时
        Args:
            target_loc (tuple): (top_left_x, top_left_y)
            target_size (tuple): (w, h)
        Returns:
            tuple: ((tl_x, tl_y), (br_x, br_h))
        """
        x, y, w, h = roi

        space = round(min(w, h) * 0.5)

        ax, ay = x - space, y - space  # 扩大一半
        aw, ah = w + 2 * space, h + 2 * space

        area = (ax, ay, aw, ah)
        return area

    def format_point(self, point) -> tuple:
        x, y = point[0], point[1]

        # ensure the point in within the screen size
        x = x if x >= 0 else 0
        y = y if y >= 0 else 0

        x = x if x < 1280 else 1279
        y = y if y < 720 else 719

        return (x, y)

    def write_output(self, filename: str) -> None:
        if self.screenshot is None:
            return
        cv2.imwrite(f'{Path.cwd()}/{filename}.png', self.screenshot)

    def write_json(self, content, name) -> None:
        """
        :param config_name: no ext
        :param data: dict
        :return:
        """
        filepath = Path.cwd() / f"{name}.json"
        with open(filepath, 'w') as fp:
            json.dump(content, fp, indent=2)


# if __name__ == "__main__":
#     print(f"args: {sys.argv}")
#     from pathlib import Path
#     sys.path.append(str(Path(__file__).parent.parent.parent))

#     if len(sys.argv) > 1:
#         if len(sys.argv) == 2:
#             target = sys.argv[1]   # path of target image
#             emulator = Emulator(config_name="osa")
#             device = emulator.main_device
#             screenshot = device.get_screenshot()
#         else:
#             screenshot = cv2.imread(sys.argv[1])
#             target = sys.argv[2]

#         if screenshot is None:
#             logger.error("Error: Failed to get screenshot")
#             sys.exit(1)
#         pro = ImageProcessor(screenshot)
#         result = pro.parse_image_file(target)
#         logger.background(json.dumps(result))
#         pro.write_output(f"output")
#     else:
#         emulator = Emulator(config_name="osa")
#         device = emulator.main_device
#         screenshot = device.get_screenshot()
#         if screenshot is None:
#             logger.error("Error: Failed to get screenshot")
#             sys.exit(1)
#         pro = ImageProcessor(screenshot)
#         pro.write_output(f"output-i")
