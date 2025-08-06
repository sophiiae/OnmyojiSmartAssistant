import random
import sys
from module.base.logger import logger
from module.base.exception import RequestHumanTakeover
from module.config.enums import BuffClass
from module.image_processing.rule_image import RuleImage
from tasks.battle.battle import Battle
from tasks.exploration.assets import ExplorationAssets as EA
from tasks.general.assets import GeneralAssets as GA
from tasks.general.page import page_exp, page_main

class ExpBase(EA, Battle):
    name = "Exploration"
    is_buff_on = False

    def auto_backup(self):
        success = False
        # 进入自动轮换阵容设置
        success = self.add_backup_shiki()

        if not success:
            logger.error("Failed to add backup")
            self.exit_chapter()

        logger.info("Successfully added backup")

    def add_backup_shiki(self) -> bool:
        success = True
        # 进入候补设置
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_BACKUP_PAGE_CHECK):
                break

            if self.appear(self.I_BACKUP_CONFIG):
                self.click(self.I_BACKUP_CONFIG)

        # 清空狗粮
        while 1:
            image = self.wait_and_shot()
            backup_count, total = self.O_BACKUP_COUNT.digit_counter(image)
            if backup_count < 10:
                break

            self.click(self.I_BACKUP_CLEAR)

        # 点击候补出战框
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_BACKUP_FOCUS, 0.95):
                break
            self.click(self.C_BACKUP_FRAME_TOP)

        # 选择狗粮类型
        # TODO: 根据设置选择式神类型
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_SHIKI_MATERIAL_SELECTED):
                break

            if self.appear(self.I_SHIKI_MATERIAL):
                self.click(self.I_SHIKI_MATERIAL)
                continue

            if self.appear(self.I_SHIKI_ALL):
                self.click(self.I_SHIKI_ALL)

        # 加狗粮
        retry = 0
        while 1:
            image = self.wait_and_shot()
            backup_count, total = self.O_BACKUP_COUNT.digit_counter(image)
            if backup_count is None or retry > 5:
                return False

            if backup_count > 40:
                break

            self.add_material_shiki()
            retry += 1

        # 确认
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_BACKUP_CONFIRM):
                break
            self.click(self.I_BACKUP_CONFIRM)

        return success

    def add_material_shiki(self):
        total = 0
        white_count = 2

        while total < 5:
            self.wait_and_shot(1)

            if self.appear(self.I_M_RED):
                self.long_click(self.I_M_RED)
                total += 1

            if white_count > 0 and self.appear(self.I_M_WHITE):
                self.long_click(self.I_M_WHITE)
                total += 1
                white_count -= 1

            self.swipe(self.S_SHIKI_TO_LEFT)

    def exit_chapter(self):
        self.wait_and_shot()
        if not self.appear(self.I_EXP_C_CHAPTER):
            return

        # 退出章节探索
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_EXP_CHAPTER_DISMISS_ICON):
                break

            if self.appear(self.I_EXP_CHAPTER_EXIT_CONFIRM):
                self.click(self.I_EXP_CHAPTER_EXIT_CONFIRM)
                continue

            if self.appear(self.I_EXP_CHAPTER_EXIT):
                self.click(self.I_EXP_CHAPTER_EXIT)

        # 关闭章节探索弹窗
        while 1:
            self.wait_and_shot()
            if self.appear(GA.I_C_EXP):
                break

            if self.appear(self.I_EXP_CHAPTER_DISMISS_ICON):
                self.click(self.I_EXP_CHAPTER_DISMISS_ICON)
                continue

        self.close_config_buff()
        self.goto(page_main, page_exp)
        raise RequestHumanTakeover()

    def soul_clear(self):
        self.enter_shiki_book(self.I_SHIKI_BOOK_ENT)

        # 进入御魂页面
        pos = 1
        while 1:
            logger.info("Entered soul page")
            self.wait_and_shot()
            if self.appear(self.I_SOUL_GREED):
                break

            if pos == 1:
                self.click(self.C_SOUL_ENT_POS1)
                pos += 1
            elif pos == 2:
                self.click(self.C_SOUL_ENT_POS2)
                pos += 1
            else:
                self.click(self.C_SOUL_ENT_POS3)

        # 进入贪吃鬼小屋
        while 1:
            logger.info("Entered soul greed house")
            self.wait_and_shot()
            if self.appear(self.I_SOUL_GREED_EAT):
                break

            if self.appear(self.I_SOUL_GREED_CHECK):
                self.click(self.C_SOUL_EAT_HABIT)
                continue

            if self.appear(self.I_SOUL_GREED):
                self.click(self.I_SOUL_GREED)

        # 进食御魂
        for _ in range(2):
            logger.info("Start eating souls...")
            self.wait_and_shot()

            if self.appear(self.I_SOUL_GREED_EAT_CONFIRM, 0.95):
                self.click(self.C_SOUL_EAT_COMFIRM_CHECKBOX)
                self.click(self.I_SOUL_GREED_EAT_CONFIRM)
                break

            if self.appear(self.I_SOUL_GREED_EAT):
                self.click(self.I_SOUL_GREED_EAT)

        # 随机点击，退出贪吃鬼
        action_click = random.choice(
            [self.C_REWARD_1, self.C_REWARD_2])
        self.click(action_click)

        # 关闭贪吃鬼小屋
        while 1:
            logger.info("Exit soul greed house")
            self.wait_and_shot()
            if not self.appear(self.I_SOUL_GREED_CHECK):
                break

            if self.appear(self.I_SOUL_GREED_CLOSE):
                self.click(self.I_SOUL_GREED_CLOSE)

        self.exit_shiki_book(self.I_EXP_C_CHAPTER)

    def open_config_buff(self):
        self.exp_config = self.config.model.exploration

        buff = []
        config = self.exp_config.exploration_config
        if config.buff_gold_50:
            buff.append(BuffClass.GOLD_50)
        if config.buff_gold_100:
            buff.append(BuffClass.GOLD_100)
        if config.buff_exp_50:
            buff.append(BuffClass.EXP_50)
        if config.buff_exp_100:
            buff.append(BuffClass.EXP_100)

        return self.check_buff(buff, page_exp)

    def close_config_buff(self):
        buff = []
        config = self.exp_config.exploration_config
        if config.buff_gold_50:
            buff.append(BuffClass.GOLD_50_CLOSE)
        if config.buff_gold_100:
            buff.append(BuffClass.GOLD_100_CLOSE)
        if config.buff_exp_50:
            buff.append(BuffClass.EXP_50_CLOSE)
        if config.buff_exp_100:
            buff.append(BuffClass.EXP_100_CLOSE)

        return self.check_buff(buff, page_exp)

    def toggle_exp_team_lock(self, lock: bool = True):
        return self.toggle_team_lock(self.I_EXP_TEAM_LOCK, self.I_EXP_TEAM_UNLOCK, lock)
