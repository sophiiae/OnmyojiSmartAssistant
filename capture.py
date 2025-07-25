from pathlib import Path
import sys
from module.base.logger import logger
from module.control.server.data_collector import DataCollector

if __name__ == "__main__":
    # for screenshot
    if len(sys.argv) < 3:
        logger.error("Missing config name or save file name or type")
        logger.warning(
            "Format: py ./capture.py [config_name] [file_name]")
    else:
        # example:  py .\capture.py qian e2
        name, file = sys.argv[1:]
        d = DataCollector(config_name=name)

        filepath = f"data/screenshots/{file}.cap.png"
        d.capture_screenshot(filepath)
