import time
from module.base.logger import logger
from module.image_processing.rule_image import RuleImage
from tasks.components.clean_souls.assets import CleanSoulsAssets
from tasks.task_base import TaskBase

class CleanSouls(TaskBase, CleanSoulsAssets):
    name = 'CleanSouls'

    def clean_souls(self):
        self.enter_soul_page()
        self.feed_low_lv_souls()
        # self.tidy_up_souls()

    def enter_soul_page(self):
        # 进入御魂页面
        pos = 1
        while 1:
            logger.info("Entered soul page")
            self.wait_and_shot()
            if self.appear(self.I_SOUL_GREED, 0.95):
                break

            if pos == 1:
                self.click(self.C_SOUL_ENT_POS1)
                pos += 1
            elif pos == 2:
                self.click(self.C_SOUL_ENT_POS2)
                pos += 1
            else:
                self.click(self.C_SOUL_ENT_POS3)

    def feed_low_lv_souls(self):
        # 进入贪吃鬼小屋
        while 1:
            logger.info("Entered soul greed house")
            self.wait_and_shot()
            if self.appear(self.I_SOUL_GREED_EAT):
                break

            if self.appear(self.I_SOUL_GREED_CHECK):
                self.click(self.C_SOUL_EAT_HABIT)
                continue

            self.appear_then_click(self.I_SOUL_GREED)

        # 进食御魂
        for _ in range(2):
            logger.info("Start eating souls...")
            self.wait_and_shot()

            if self.appear(self.I_SOUL_GREED_EAT_CONFIRM, 0.95):
                self.click(self.C_SOUL_EAT_COMFIRM_CHECKBOX)
                self.click(self.I_SOUL_GREED_EAT_CONFIRM)
                break

            self.appear_then_click(self.I_SOUL_GREED_EAT)

        # 随机点击，退出贪吃鬼
        self.click(self.C_RANDOM_CLICK)

        # 关闭贪吃鬼小屋
        while 1:
            logger.info("Exit soul greed house")
            self.wait_and_shot()
            if not self.appear(self.I_SOUL_GREED_CHECK):
                break

            self.appear_then_click(self.I_SOUL_GREED_CLOSE)

    def tidy_up_souls(self):
        self.enter_scheme_page()
        self.use_schemes()

    def enter_scheme_page(self):
        # 进入整理页面
        while 1:
            self.class_logger(self.name, "Entering tidy up page")
            self.wait_and_shot()
            if self.appear(self.I_MASS_UPGRADE_ICON):
                break
            self.click(self.C_TIDY_UP_LANTERN)

        # 进入方案页面
        while 1:
            self.wait_and_shot()
            self.class_logger(self.name, "Entering scheme page")
            if self.appear(self.I_SCHEME_IMPORT_ICON):
                break

            self.click(self.C_SCHEMES)

    def action_on_all(self, action: RuleImage):
        self.class_logger(self.name, "Select all schemes and souls")
        # 选择全部方案
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_SELECT_ALL_SCHEMES):
                break

            self.click(self.I_SELECT_ALL_SCHEMES)

        # 选择全部御魂
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_SELECT_ALL_SOULS):
                break
            self.click(self.I_SELECT_ALL_SOULS)

        while 1:
            self.wait_and_shot()
            if self.appear(self.I_EMPTY_LANTERN):
                break

            self.appear_then_click(self.I_B_CONFIRM_WIDE)
            time.sleep(0.3)
            self.click(action)

    def use_schemes(self):
        # 选择弃置方案
        while 1:
            self.class_logger(self.name, "Select dump schemes")
            self.wait_and_shot()
            if self.appear(self.I_DUMP_ICON):
                break

            self.click(self.C_DUMP_SCHEME)

        self.action_on_all(self.I_DUMP_ICON)

        # 进入已弃置
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_RECOVER, 0.95):
                break
            self.click(self.C_DUMPED_SOULS)

        # 选择强化方案
        while 1:
            self.wait_and_shot()
            if self.appear_then_click(self.I_SCHEME_3, 0.95):
                break
            self.click(self.C_UPGRADE_SCHEME)

        self.action_on_all(self.I_RECOVER)

    def donat_dumped_souls(self):
        # TODO
        pass
