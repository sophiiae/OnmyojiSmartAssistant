import json
import cv2
from pathlib import Path
import sys
from module.base.logger import logger
from module.image_processing.image_processor import ImageProcessor
from module.control.server.device import Device

def match_in_file(screenshot_path, target):
    screenshot = cv2.imread(screenshot_path)
    pro = ImageProcessor(screenshot)
    result = pro.parse_image_file(target)
    print(json.dumps(result))
    pro.write_output(f"output")

def match_in_simulator(target):
    device = Device("127.0.0.1:16384")
    screenshot = device.get_screenshot()
    pro = ImageProcessor(screenshot)
    result = pro.parse_image_file(target)
    print(json.dumps(result))
    pro.write_output(f"output")


if __name__ == "__main__":
    # match target
    if len(sys.argv) > 2:
        match_in_file(sys.argv[1], sys.argv[2])
    else:
        match_in_simulator(sys.argv[1])
