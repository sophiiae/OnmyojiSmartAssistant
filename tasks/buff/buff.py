import time
import cv2
from pathlib import Path

from module.base.logger import logger
from module.image_processing.rule_ocr import RuleOcr
from module.image_processing.rule_image import RuleImage
from tasks.buff.assets import BuffAssets
from tasks.task_base import TaskBase
from tasks.general.page import Page
from tasks.general.page import page_main, page_exp, page_minamoto


class Buff(TaskBase, BuffAssets):

    def open_buff(self, page: Page = page_main):
        """
        打开buff的总界面
        :return:
        """
        logger.info('Open buff')

        match_open = {
            page_main: self.I_BUFF_OPEN,
            page_exp: self.I_EXP_BUFF_OPEN,
            page_minamoto: self.I_MINAMOTO_BUFF_OPEN
        }
        open_button = match_open[page]

        while 1:
            time.sleep(0.3)
            self.screenshot()
            if self.appear(self.I_BUFF_CLOUD, 0.95):
                break

            if self.appear_then_click(open_button):
                continue

    def close_buff(self):
        """
        关闭buff的总界面, 但是要确保buff界面已经打开了
        :return:
        """
        logger.info('Close buff')

        while 1:
            time.sleep(0.3)
            self.screenshot()
            if self.click_static_target(self.I_BUFF_CLOUD):
                continue

    def deactivate_buff(self, buff: list):
        if 'buff_awake' in buff:
            self.click_static_target(self.I_BUFF_AWAKE_ACTIVATE)
        if 'buff_soul' in buff:
            self.click_static_target(self.I_BUFF_SOUL_ACTIVATE)
        if 'buff_gold_50' in buff:
            self.click_static_target(self.I_BUFF_GOLD_50_ACTIVATE)
        if 'buff_gold_100' in buff:
            self.click_static_target(self.I_BUFF_GOLD_100_ACTIVATE)
        if 'buff_exp_50' in buff:
            self.click_static_target(self.I_BUFF_EXP_50_ACTIVATE)
        if 'buff_exp_100' in buff:
            self.click_static_target(self.I_BUFF_EXP_100_ACTIVATE)

    def activate_buff(self, buff: list):
        if 'buff_awake' in buff:
            self.click_static_target(self.I_BUFF_AWAKE_DEACTIVATE)
        if 'buff_soul' in buff:
            self.click_static_target(self.I_BUFF_SOUL_DEACTIVATE)
        if 'buff_gold_50' in buff:
            self.click_static_target(self.I_BUFF_GOLD_50_DEACTIVATE)
        if 'buff_gold_100' in buff:
            self.click_static_target(self.I_BUFF_GOLD_100_DEACTIVATE)
        if 'buff_exp_50' in buff:
            self.click_static_target(self.I_BUFF_EXP_50_DEACTIVATE)
        if 'buff_exp_100' in buff:
            self.click_static_target(self.I_BUFF_EXP_100_DEACTIVATE)

    def get_area(self, buff: RuleOcr) -> tuple | None:
        """
        获取要点击的开关buff的区域
        :param cls:
        :param image:
        :param buff:
        :return:  如果没有就返回None
        """
        self.screenshot()
        if self.device.screenshot is None:
            logger.warning('Failed to take screenshot')
            return None

        area = buff.ocr_full(self.device.screenshot)

        if area == tuple([0, 0, 0, 0]):
            logger.info(f'No {buff.name} buff')
            return None

        # 开始的x坐标就是文字的右边
        start_x = area[0] + area[2] + 10  # 10是文字和开关之间的间隔
        start_y = area[1] - 10
        width = 80  # 开关的宽度 80够了
        height = area[3] + 20
        return int(start_x), int(start_y), int(width), int(height)

    