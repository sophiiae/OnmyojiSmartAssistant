import time
import sys
from module.base.logger import logger
from module.base.exception import RequestHumanTakeover
from module.config.enums import BuffClass
from tasks.exploration.assets import ExplorationAssets as EA
from tasks.components.page.page import page_exp, page_main
from tasks.components.battle.battle import Battle

class ExpBase(EA, Battle):
    name = "Exploration"
    is_buff_on = False

    def post_chapter_battle(self):
        # 检查章节奖励
        if self.get_chapter_reward():
            time.sleep(1)

        time.sleep(2)
        while 1:
            self.wait_and_shot()
            if self.appear_then_click(self.I_EXP_CHAPTER_DISMISS_ICON, 0.95):
                time.sleep(1)
                continue

            # 如果回到了探索界面 -> 检查宝箱
            if self.appear(self.I_C_EXP):
                self.check_treasure_box()
                break

            # 如果有妖气封印，就关闭
            if self.appear(self.I_EXP_YAOQI):
                self.appear_then_click(self.I_EXP_YAOQI_CLOSE)

    def get_chapter_reward(self):
        found = False
        while 1:
            self.wait_and_shot(1)
            if not self.appear(self.I_EXP_C_CHAPTER, 0.95):
                break

            if self.appear(self.I_GAIN_REWARD):
                self.random_click_right()
                found = True
                continue

            self.appear_then_click(self.I_EXP_CHAP_REWARD)

        if found:
            self.class_logger(self.name, "Got all chapter reward.")
        return found

    def check_treasure_box(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_EXP) and not self.appear(self.I_EXP_TREASURE_BOX, 0.95):
                break

            if self.click_static_target(self.I_EXP_TREASURE_BOX, 0.95):
                got_reward = self.wait_until_appear(
                    self.I_REWARD, 3)

                if got_reward:   # 领取宝箱物品
                    time.sleep(0.4)
                    self.random_click_right()
                    continue

            # 如果有妖气封印，就关闭
            if self.appear(self.I_EXP_YAOQI):
                self.appear_then_click(self.I_EXP_YAOQI_CLOSE)

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

            self.appear_then_click(self.I_BACKUP_CONFIG)

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

            if self.appear_then_click(self.I_SHIKI_MATERIAL):
                continue

            self.appear_then_click(self.I_SHIKI_ALL)

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

    def exit_chapter(self, raise_exception=False):
        self.wait_and_shot()
        if not self.appear(self.I_EXP_C_CHAPTER, 0.95):
            return

        # 退出章节探索
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_EXP_CHAPTER_DISMISS_ICON):
                break

            if self.appear_then_click(self.I_EXP_CHAPTER_EXIT_CONFIRM, 0.95):
                continue

            self.appear_then_click(self.I_EXP_CHAPTER_EXIT)

        # 关闭章节探索弹窗
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_EXP):
                break

            self.appear_then_click(self.I_EXP_CHAPTER_DISMISS_ICON)

        if raise_exception:
            self.close_config_buff()

        if not self.check_page_appear(page_main, 0.97):
            self.goto(page_main)

        if raise_exception:
            raise RequestHumanTakeover()

    def soul_clear(self):
        self.enter_shiki_book(self.I_SHIKI_BOOK_ENT)
        self.clean_souls()
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
