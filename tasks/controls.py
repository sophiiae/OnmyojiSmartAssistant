from datetime import datetime
from datetime import datetime
from functools import cached_property
from typing import Union
import numpy as np
import time
from typing import Optional

from module.control.server.device import Device
from module.config.config import Config
from tasks.components.page.assets import PageAssets
from tasks.components.page.page_map import PageMap
from tasks.components.widgets.assets import WidgetsAssets
from tasks.subaccounts.assets import SubaccountsAssets
from module.image_processing.rule_click import RuleClick
from module.image_processing.rule_image import RuleImage
from module.image_processing.rule_ocr import RuleOcr
from module.image_processing.rule_swipe import RuleSwipe
from module.base.logger import logger
from module.base.timer import Timer
from module.base.exception import RequestHumanTakeover

class Controls(PageAssets, SubaccountsAssets, PageMap, WidgetsAssets):
    config: Config
    device: Device
    image = None

    def __init__(self, device: Device) -> None:
        self.device = device
        self.config = device.config

        self.start_time = datetime.now()  # 启动的时间

    def _burst(self) -> bool:
        """
        游戏界面突发异常检测
        :return: 没有出现返回False, 其他True
        """

        self.check_request_invitation()
        return True

    @cached_property
    def ui_close(self):
        return [
            self.I_B_BLUE_LEFT_ANGLE,
            self.I_B_RED_X,
            self.I_B_YELLOW_LEFT_ANGLE
        ]

    @cached_property
    def accept_request_map(self):
        return {
            'accept_jade': [self.I_QUEST_JADE],
            'accept_ap': [self.I_QUEST_AP],
            'accept_pet_food': [self.I_QUEST_DOG, self.I_QUEST_CAT],
        }

    def check_request_invitation(self):
        if not self.appear(self.I_QUEST_ACCEPT):
            return False

        # 查看设置
        quest_config = self.config.model.wanted_quests.accept_quest_config
        accept_types = [
            k for k, v in quest_config.model_dump().items() if v is True]

        # 如果任何类型都不接受直接返回
        if not accept_types:
            return False

        accept_targets = []
        for type, imgs in self.accept_request_map.items():
            if type in accept_types:
                accept_targets.extend(imgs)

        # 查看邀请符不符合设置
        click_button = self.I_QUEST_IGNORE
        for t in accept_targets:
            if self.appear(t, 0.96):
                click_button = self.I_QUEST_ACCEPT
                break

        while 1:
            time.sleep(0.3)
            self.device.get_screenshot()
            if not self.appear(target=click_button, threshold=0.96):
                logger.info('Handled invitation.')
                break

            self.appear_then_click(click_button, threshold=0.96)
        return True

    def appear(self, target: RuleImage, threshold: float = 0.9, delay: float = 0.1) -> bool:
        if not isinstance(target, RuleImage):
            return False
        time.sleep(0.1)
        screenshot = self.device.screenshot
        if screenshot is None:
            screenshot = self.screenshot()
        return target.match_target(screenshot, threshold)

    def wait_and_shot(self, wait_time=0.3):
        time.sleep(wait_time)
        return self.screenshot()

    def wait_click_if_appear(self, target: RuleImage, wait_time=0.3):
        self.wait_and_shot(wait_time)

        if self.appear(target):
            self.click(target)

    def wait_until_click(self,
                         target: RuleImage, limit: float = 5, interval: float = 0.3,
                         delay: float = 0.3, wait_after: float = 0.5,
                         threshold: float = 0.9) -> bool:
        """等待出现了再点击，用于不移动的图标

        Args:
            target (RuleImage): 
            limit (float, optional): waiting time limit (s). Defaults to 5.
            interval (float, optional): interval between retry. Defaults to 0.4.
            delay (float, optional): Defaults to 0.5.
            wait_after (float, optional): Defaults to 0.8.
            threshold (float, optional): Defaults to 0.9.
        """

        if self.wait_until_appear(target, limit, interval, threshold=threshold):
            time.sleep(delay)
            self.appear_then_click(target)
            time.sleep(wait_after)
            return True

        logger.critical(f"Not able to find and click {target.name}.")
        raise RequestHumanTakeover(
            f"Not able to find and click {target.name}.")

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

    def appear_then_click(self,
                          target: RuleImage,
                          threshold: float = 0.9,
                          delay: float = 0.1
                          ) -> bool:
        """出现就点击，用于会移动的怪物/图标
        Args:
            target (RuleImage): _description_
            threshold (float, optional): _description_. Defaults to 0.9.
        """
        if self.appear(target, threshold=threshold):
            time.sleep(delay)
            self.click(target)
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

        raise RequestHumanTakeover(
            f"Wait until appear {pass_t.name} or {fail_t.name} timeout")

    def screenshot(self):
        """截图 引入中间函数的目的是 为了解决如协作的这类突发的事件

        Returns:
            np.array: image
        """
        self.image = self.device.get_screenshot()
        # 判断突发事件
        self._burst()
        return self.image

    def swipe(self, swipe: RuleSwipe, duration: int = 400) -> None:
        """swipe

        Args:
            swipe (RuleSwipe): 
            interval (float, optional): Defaults to None.
            duration (int, optional): [200,800] Defaults to 400. 数值越大越慢，越小越快
        """
        if not isinstance(swipe, RuleSwipe):
            return

        logger.info(f"[Swipe] Executing Swipe for {swipe.name}")
        sx, sy, ex, ey = swipe.coord()
        self.device.swipe(start_x=sx, start_y=sy, end_x=ex,
                          end_y=ey, duration=duration)

    def click(self, target: Union[RuleImage, RuleClick]):
        """click

        Args:
            target (RuleImage):
            interval (float, optional): Defaults to None.

        Returns:
            bool:
        """
        x, y = target.coord()
        self.device.click(x=x, y=y)
        time.sleep(0.5)

    def long_click(self, target: Union[RuleImage, RuleClick]) -> None:
        """
        :param control_name:
        :param x:
        :param y:
        :param duration: 单位是s
        :return:
        """
        x, y = target.coord()
        self.device.long_click(x, y)
        time.sleep(0.5)

    def find_ocr_target(self, target: RuleOcr) -> bool:
        """
        找到ocr目标，如果目标存在，则返回True，否则返回False
        """
        area = target.ocr_full(self.screenshot(), keyword=target.keyword)
        return area != (0, 0, 0, 0)

    def ocr_appear_click(self, target: RuleOcr) -> bool:
        """
        ocr识别目标，如果目标存在，则触发动作
        :param target:
        :param action:
        :return:
        """
        if not self.find_ocr_target(target):
            return False
        self.ocr_click(target)
        return True

    def ocr_click(self, target: RuleOcr):
        x, y = target.coord()
        self.device.click(x, y)

    def random_click_right(self, click_delay=0.2):
        """Perform random click within screen
        """
        time.sleep(click_delay)
        x = np.random.randint(990, 1260)
        y = np.random.randint(180, 550)
        self.device.click(x=x, y=y)

    def click_until_disappear(self, target: RuleImage, interval: float = 1):
        """点击一个按钮直到消失

        Args:
            target (RuleImage):
            interval (float, optional): Defaults to 1.
        """
        while 1:
            self.screenshot()
            if not self.appear(target):
                break
            elif self.wait_until_appear(target):
                continue

    def click_static_target(self, target: RuleImage, threshold: float = 0.9, delay: float = 0.5, retry: int = 5):
        """
        点击静态的图标，比如按钮
        """
        for _ in range(retry):
            self.wait_and_shot()
            if not self.appear(target, threshold=threshold):
                return True
            self.appear_then_click(target, threshold=threshold)
            time.sleep(delay)
        return False

    def click_moving_target(self, target: RuleImage, fail_check: RuleImage, threshold: float = 0.9):
        """
        点击移动的图标，比如怪物
        """
        while 1:
            self.wait_and_shot(0.1)
            if not self.appear(fail_check, threshold=threshold):
                return True
            self.appear_then_click(target, threshold=threshold)
        return False

    def set_next_run(self, task: str, finish: bool = False,
                     success: Optional[bool] = None, target_time: Optional[datetime] = None) -> None:
        if finish:
            start_time = datetime.now().replace(microsecond=0)
        else:
            start_time = self.start_time
        self.config.task_delay(task, start_time=start_time,
                               success=success, target_time=target_time)
