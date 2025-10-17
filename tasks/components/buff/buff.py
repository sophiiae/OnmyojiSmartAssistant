import time
import cv2
from pathlib import Path

from module.base.logger import logger
from module.image_processing.rule_ocr import RuleOcr
from module.image_processing.rule_image import RuleImage
from tasks.components.buff.assets import BuffAssets
from tasks.task_base import TaskBase
from tasks.components.page.page import Page
from tasks.components.page.page import page_main, page_exp, page_minamoto

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
            if self.appear(self.I_BUFF_AWAKE, 0.95):
                break

            self.appear_then_click(open_button)
        time.sleep(0.5)

    def close_buff(self):
        """
        关闭buff的总界面, 但是要确保buff界面已经打开了
        :return:
        """
        logger.info('Close buff')

        while 1:
            time.sleep(0.3)
            self.screenshot()
            if not self.appear(self.I_BUFF_AWAKE, 0.95):
                break
            self.appear_then_click(self.I_BUFF_CLOUD)

    def get_area(self, buff: RuleOcr, activate: bool) -> tuple | None:
        """
        获取要点击的开关buff的区域
        :param cls:
        :param image:
        :param buff:
        :return:  如果没有就返回None
        """
        img = self.screenshot()

        # 已经启动的buff就不用再重新查找了，roi在开启的时候就更新了
        if activate:
            area = buff.ocr_full(img)

            if area == tuple([0, 0, 0, 0]):
                logger.info(f'No {buff.name} buff')
                return None

        x = 775  # 开关最左边
        y = max(0, buff.roi[1] - 10)  # 确保y坐标不为负数
        w = 80  # 增加开关的宽度
        h = 80  # 增加开关的高度

        logger.info(
            f"Get target area: {(x, y, w, h)}")

        # # 测试用
        # cv2.rectangle(self.device.image, (x, y),
        #               (x + w, y + h), (101, 67, 196), 2)
        # cv2.imwrite(f'{Path.cwd()}/area.png', self.device.image)

        return x, y, w, h

    def set_switch_area(self, area):
        """
        设置开关的区域
        :param area:
        :return:
        """
        self.I_BUFF_OPEN_YELLOW.area = tuple(area)  # 动态设置area
        self.I_BUFF_CLOSE_RED.area = tuple(area)

    def toggle_buff(self, activate: bool = True):
        if activate:
            logger.info("Activating buff")
            while 1:
                self.wait_and_shot()
                if not self.appear(self.I_BUFF_CLOSE_RED, 0.95):
                    return

                self.appear_then_click(self.I_BUFF_CLOSE_RED)
        else:
            logger.info("Deactivating buff")
            while 1:
                self.wait_and_shot()
                if not self.appear(self.I_BUFF_OPEN_YELLOW, 0.95):
                    return

                self.appear_then_click(self.I_BUFF_OPEN_YELLOW)

    def awake(self, activate: bool = True):
        """
        觉醒buff
        :param activate: 是否打开
        :return:
        """
        logger.info('Awake buff')
        self.wait_and_shot()
        area = self.get_area_image(self.I_BUFF_AWAKE)
        if not area:
            logger.warning('No awake buff')
            return None
        self.set_switch_area(area)
        self.toggle_buff(activate)

    def soul(self, activate: bool = True):
        """
        御魂buff
        :param activate: 是否打开
        :return:
        """
        logger.info('Soul buff')
        self.wait_and_shot()
        area = self.get_area_image(self.I_BUFF_SOUL)
        if not area:
            logger.warning('No soul buff')
            return None
        self.set_switch_area(area)
        self.toggle_buff(activate)

    def gold_50(self, activate: bool = True):
        """
        金币50buff
        :param activate: 是否打开
        :return:
        """
        logger.info('Gold 50 buff')
        if self.find_target_buff(self.O_GOLD_50, activate):
            self.toggle_buff(activate)

    def gold_100(self, activate: bool = True):
        """
        金币100buff
        :param activate: 是否打开
        :return:
        """
        logger.info('Gold 100 buff')
        if self.find_target_buff(self.O_GOLD_100, activate):
            self.toggle_buff(activate)

    def exp_50(self, activate: bool = True):
        """
        经验50buff
        :param activate: 是否打开
        :return:
        """
        logger.info('Exp 50 buff')
        if self.find_target_buff(self.O_EXP_50, activate):
            self.toggle_buff(activate)

    def exp_100(self, activate: bool = True):
        """
        经验100buff
        :param activate: 是否打开
        :return:
        """
        logger.info('Exp 100 buff')
        if self.find_target_buff(self.O_EXP_100, activate):
            self.toggle_buff(activate)

    def find_target_buff(self, target: RuleOcr, activate: bool) -> bool:
        retry = 0
        while 1:
            self.wait_and_shot()
            area = self.get_area(target, activate)
            if retry > 3:
                logger.warning(f'Cannot find {target.name} buff')
                return False

            if area:
                self.set_switch_area(area)
                return True

            self.swipe(self.S_BUFF_DOWN)
            retry += 1
        return True

    def get_area_image(self, target: RuleImage) -> list | None:
        """
        获取觉醒加成或者是御魂加成所要点击的区域
        因为实在的图片比ocr快
        :param image:
        :param target:
        :return:
        """
        self.device.get_screenshot()
        if not self.appear(target):
            logger.warning(f'No {target.name} buff')
            return None
        x = int(target.roi_center()[0] + 364)
        y = int(target.roi[1])
        w = 80
        h = int(target.roi[3])

        # # 测试用
        # cv2.rectangle(self.device.image, (x, y),
        #               (x + w, y + h), (101, 67, 196), 2)
        # cv2.imwrite(f'{Path.cwd()}/area.png', self.device.image)
        return [x, y, w, h]
