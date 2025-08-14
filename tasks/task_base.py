from datetime import datetime
from functools import cached_property
from typing import Union
import numpy as np
import time
from typing import Optional

from module.base.exception import GamePageUnknownError

from module.image_processing.rule_click import RuleClick
from module.image_processing.rule_image import RuleImage
from tasks.components.widgets.assets import WidgetsAssets
from module.control.server.device import Device
from module.base.timer import Timer
from module.base.logger import logger
from tasks.components.page.page import *
from tasks.controls import Controls

class TaskBase(Controls):
    def __init__(self, device: Device) -> None:
        super().__init__(device)

    def wait_request(self):
        self.device.get_screenshot()
        self.check_request_invitation()

    def check_page_appear(self, page, check_delay: float = 0.01):
        """
        判断当前页面是否为page
        """
        time.sleep(check_delay)
        if not self.wait_until_appear(page.check_button, 1, threshold=0.95):
            logger.warning(f"Not in {page.name} page")
            return False
        return True

    def is_scroll_closed(self):
        """
        判断庭院界面卷轴是否打开
        """
        return self.appear(WidgetsAssets.I_SCROLL_CLOSE)

    def get_current_page(self) -> Page:
        timeout = Timer(5, 20).start()
        logger.info("Getting current page")

        while 1:
            self.screenshot()

            # 如果20S还没有到底，那么就抛出异常
            if timeout.reached():
                break

            for page in self.MAP.keys():
                if page.check_button is None:
                    continue
                if self.check_page_appear(page=page):
                    logger.info(f"[UI]: {page.name}")
                    self.ui_current = page
                    return page

            # Try to close unknown page
            for close in self.ui_close:
                if self.wait_until_click(close):
                    logger.warning('Trying to switch to supported page')
                    timeout = Timer(5, 10).start()
                time.sleep(0.2)
        logger.critical("Starting from current page is not supported")
        raise GamePageUnknownError

    def goto(self, destination: Page, current: Page | None = None):
        if not current:
            self.get_current_page()
            current = self.ui_current

        path = self.find_path(current, destination)
        if path is None:
            logger.error(
                f"No path found from {current.name} to {destination.name}")
            return

        logger.info(f"[PATH] Start following the path: {
                    [p.name for p in path]}")

        for idx, page in enumerate(path):
            # 已经到达页面，退出
            if page == destination:
                logger.info(f'[UI] Page arrive: {destination}')
                return

            while 1:
                self.screenshot()
                if self.check_page_appear(path[idx + 1]):
                    break

                button = page.links[path[idx + 1]]
                if isinstance(button, RuleClick):
                    self.click(button)
                    time.sleep(1)

                elif isinstance(button, RuleImage):
                    if self.wait_until_click(button, interval=0.2):
                        logger.info(f"[PATH] Heading from {
                                    page.name} to {path[idx + 1].name}.")
                else:
                    raise GamePageUnknownError(
                        "Unable to identify the page button")

                time.sleep(0.2)
