from datetime import datetime
from typing import Union
import numpy as np
import time

from module.base.exception import RequestHumanTakeover
from module.control.config.config import Config
from module.image_processing.rule_click import RuleClick
from module.image_processing.rule_image import RuleImage
from module.image_processing.rule_swipe import RuleSwipe
from tasks.main_page.assets import MainPageAssets
from module.control.server.adb_device import ADBDevice
from module.base.timer import Timer
from module.base.logger import logger


class TaskBase(MainPageAssets):
    config: Config
    device: ADBDevice

    limit_time: datetime  # 限制运行的时间，是软时间，不是硬时间
    limit_count: int  # 限制运行的次数
    current_count: int  # 当前运行的次数

    def __init__(self, config: Config, device: ADBDevice) -> None:
        """

        :rtype: object
        """
        self.config = config
        self.device = device

    def _burst(self) -> bool:
        """
        游戏界面突发异常检测
        :return: 没有出现返回False, 其他True
        """

        appear_invitation = self.appear(self.I_QUEST_ACCEPT)
        if not appear_invitation:
            return False
        logger.info('Invitation appearing')

        # 只接受勾协
        if self.appear(self.I_QUEST_JADE, 0.96) or self.appear(self.I_QUEST_CAT, 0.96) or self.appear(self.I_QUEST_DOG, 0.96):
            click_button = self.I_QUEST_ACCEPT
        elif self.appear(self.I_QUEST_VIRTUAL, 0.96):
            click_button = self.I_QUEST_ACCEPT
        else:
            click_button = self.I_QUEST_IGNORE

        while 1:
            self.device.get_screenshot()
            if not self.appear(target=click_button, threshold=0.96):
                logger.info('Deal with invitation done')
                break
            if self.appear_then_click(click_button, threshold=0.96):
                time.sleep(0.3)
                continue
        return True

    def wait_request(self) -> bool:
        self.device.get_screenshot()
        return self._burst()

    def appear(self, target: RuleImage, threshold: float = 0.9, delay: float = 0.1) -> bool:
        if not isinstance(target, RuleImage):
            return False
        time.sleep(0.1)
        screenshot = self.device.screenshot
        if screenshot is None:
            screenshot = self.screenshot()
            if screenshot is None:
                return False
        return target.match_target(screenshot, threshold)

    def wait_and_shot(self, wait_time=0.3):
        time.sleep(wait_time)
        self.screenshot()

    def appear_then_click(self,
                          target: RuleImage,
                          threshold: float = 0.9,
                          ) -> bool:
        """出现就点击，用于会移动的怪物/图标
        Args:
            target (RuleImage): _description_
            threshold (float, optional): _description_. Defaults to 0.9.
            interval (float, optional): _description_. Defaults to 1.
        """
        if not isinstance(target, RuleImage):
            return False

        appear = self.appear(target, threshold=threshold)
        if appear:
            self.click(target)
        return appear

    def wait_until_appear(self,
                          target: RuleImage, limit: float = 5,
                          interval: float = 0.4, threshold: float = 0.9
                          ) -> bool:
        """等待出现了再点击，比如需要等过场动画，减少不必要的运行消耗
        Args:
            target (RuleImage):
            limit (float, optional): waiting time limit (s). Defaults to 3.
            interval (float, optional): interval between retry. Defaults to 0.4.
            threshold (float, optional): Defaults to 0.9.
        """
        if not isinstance(target, RuleImage):
            return False

        timeout = Timer(limit + interval, 2).start()
        while not timeout.reached():
            time.sleep(interval)
            self.screenshot()
            if self.appear(target, threshold=threshold):
                return True
        return False

    def wait_for_result(self, pass_t: RuleImage, fail_t: RuleImage,
                        limit: float = 10,
                        interval: float = 0.4) -> bool:
        """判断其中一种结果出现，比如战斗胜利/失败
        Args:
            pass_t (RuleImage):
            fail_t (RuleImage):
            limit (float, optional):. Defaults to 10.
            interval (float, optional):. Defaults to 0.4.
        """

        timeout = Timer(limit).start()
        while not timeout.reached():
            time.sleep(interval)

            self.screenshot()
            if self.appear(pass_t):
                logger.info(f"---- Got Action Success Target: {pass_t.name}")
                return True
            if self.appear(fail_t):
                logger.info(f"---- Got Action failed Target: {fail_t.name}")
                return False

        logger.warning(
            f"Wait until appear {pass_t.name} or {fail_t.name} timeout")

        raise RequestHumanTakeover

    def screenshot(self):
        """截图 引入中间函数的目的是 为了解决如协作的这类突发的事件

        Returns:
            np.array: image
        """
        image = self.device.get_screenshot()
        # 判断勾协
        self._burst()
        return image

    def swipe(self, swipe: RuleSwipe, duration: int = 400) -> None:
        """swipe

        Args:
            swipe (RuleSwipe): 
            duration (int, optional): [200,800] Defaults to 300.
        """
        if not isinstance(swipe, RuleSwipe):
            return

        logger.info(f"Executing Swipe for {swipe.name}")
        sx, sy, ex, ey = swipe.coord()
        self.device.swipe(start_x=sx, start_y=sy, end_x=ex,
                          end_y=ey, duration=duration)

    def click(self, target: Union[RuleImage, RuleClick]):
        """click

        Args:
            target (RuleImage):
        """
        x, y = target.coord()
        self.device.click(x=x, y=y)

    def random_click_right(self, click_delay=0.2):
        """Perform random click within screen
        """
        time.sleep(click_delay)
        x = np.random.randint(1000, 1200)
        y = np.random.randint(200, 500)
        self.device.click(x=x, y=y)

    def click_static_target(self, target: RuleImage, threshold: float = 0.9):
        """
        点击静态的图标，比如按钮
        """
        if not isinstance(target, RuleImage):
            return False

        for _ in range(5):
            self.wait_and_shot()
            if not self.appear(target, threshold=threshold):
                return True
            self.appear_then_click(target, threshold=threshold)
        return False

    def click_moving_target(self, target: RuleImage, success_check: RuleImage, threshold: float = 0.9):
        """
        点击移动的图标，比如怪物
        """
        if not isinstance(target, RuleImage) or not isinstance(success_check, RuleImage):
            return False

        while 1:
            self.wait_and_shot(0.2)
            if self.appear(success_check, threshold=threshold):
                return True
            self.appear_then_click(target, threshold=threshold)
        return False
