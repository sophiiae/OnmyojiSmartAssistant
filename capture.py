from pathlib import Path
import sys
from module.base.logger import logger
from module.control.server.device import Device

if __name__ == "__main__":
    # for screenshot
    if len(sys.argv) < 3:
        logger.error("Missing config name or save file name")
        logger.warning("Format: py .utils.py [config_name] [file_name]")
    else:
        # example:  py .\capture.py qian e2
        name = sys.argv[1]
        file = sys.argv[2]

        d = Device(config_name=name)
        filepath = Path.cwd() / f"{file}.cap.png"
        d.capture_screenshot(filepath)
