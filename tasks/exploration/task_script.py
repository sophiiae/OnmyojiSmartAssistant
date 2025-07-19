import sys
from module.base.logger import logger
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.control.config.enums import BuffClass
from tasks.battle.battle import Battle
from tasks.exploration.assets import ExplorationAssets as EA
from tasks.general.assets import GeneralAssets as GA
from tasks.general.page import Page, page_exp, page_main, page_realm_raid

from datetime import datetime, timedelta
import time

class TaskScript(EA, Battle):
    name = "Exploration"
    is_buff_on = False

    def run(self):
        self.exp_config = self.config.model.exploration

        # 进入探索页面
        if not self.check_page_appear(page_exp):
            self.goto(page_exp)

        # 判断是否开启绘卷模式
        scroll_mode = self.exp_config.scroll_mode
        if scroll_mode.scroll_mode_enable:
            exp_count = 50
        else:
            exp_count = self.exp_config.exploration_config.count_max

        self.check_ticket()

        count = 0
        while exp_count > 0 and count < exp_count:
            # 检查票数
            self.check_ticket()

            if self.click_static_target(self.I_EXP_CHAPTER_28):
                self.click_static_target(self.I_EXP_BUTTON)

            logger.info(f"======== Round {count + 1} Exp Started =========")
            # 进入章节战斗
            self.battle_process()
            self.after_chapter_process()

            count += 1

        # 关闭章节探索提示
        self.wait_until_click(self.I_EXP_CHAPTER_DISMISS_ICON, 2)

        # 绘卷模式去探索页面，减少页面跳转
        if scroll_mode.scroll_mode_enable:
            self.goto(page_realm_raid, page_exp)
        else:
            self.goto(page_main, page_exp)
        self.set_next_run(task='Exploration', success=True, finish=False)

        raise TaskEnd(self.name)

    def after_chapter_process(self):
        time.sleep(1)
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_EXP_CHAPTER_DISMISS_ICON):
                self.click_static_target(
                    self.I_EXP_CHAPTER_DISMISS_ICON, retry=2)

            # 如果回到了探索界面 -> 检查宝箱
            if self.appear(self.I_C_EXP):
                self.check_treasure_box()
                break

            # 如果有妖气封印，就关闭
            if self.appear(self.I_EXP_YAOQI):
                self.appear_then_click(self.I_EXP_YAOQI_CLOSE)
                continue

    def check_treasure_box(self):
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_EXP_TREASURE_BOX, 0.95):
                break

            if self.click_static_target(self.I_EXP_TREASURE_BOX, 0.95):
                got_reward = self.wait_until_appear(
                    self.I_REWARD, 3)

                if got_reward:   # 领取宝箱物品
                    time.sleep(0.7)
                    self.random_click_right()

    def battle_process(self):
        # ************************* 进入设置并操作 *******************
        if not self.wait_until_appear(self.I_EXP_C_CHAPTER, 2):
            logger.warning(
                "***** Not inside chapter or battle finished.")
            raise RequestHumanTakeover

        # 进入战斗环节
        logger.info("Start battle...")
        swipe_count = 0
        while 1:
            if not self.turn_on_auto_rotate():
                self.auto_backup()
                continue

            self.wait_and_shot()

            # BOSS 挑战
            if self.appear(self.I_EXP_BOSS):
                self.click_moving_target(self.I_EXP_BOSS, self.I_EXP_C_CHAPTER)

                if self.run_easy_battle(self.I_EXP_C_CHAPTER):
                    self.get_chapter_reward()
                    break

            # 普通怪挑战
            if self.appear(self.I_EXP_BATTLE):
                self.click_moving_target(
                    self.I_EXP_BATTLE, self.I_EXP_C_CHAPTER)
                self.run_easy_battle(self.I_EXP_C_CHAPTER)
                swipe_count = 0
                continue

            self.swipe(self.S_EXP_TO_RIGHT)
            swipe_count += 1
            if swipe_count > 7:
                self.left_check()
                swipe_count = 0
            time.sleep(0.3)

        time.sleep(1)

    def turn_on_auto_rotate(self) -> bool:
        # 自动轮换功能打开
        retry = 0
        while 1:
            self.wait_and_shot()

            # 自动轮换开着 则跳过
            if self.appear(self.I_AUTO_ROTATE_ON):
                break

            if retry > 5:
                logger.warning("Running out of backup!")
                return False

            # 自动轮换关着 则打开
            if self.appear_then_click(self.I_AUTO_ROTATE_OFF):
                retry += 1
                continue

        return True

    def auto_backup(self):
        success = False
        # TODO: add logic for adding backup
        # 进入自动轮换阵容设置
        # success = self.add_backup_shiki()

        if not success:
            logger.error("Failed to add backup")
            self.exit_chapter()

    def add_backup_shiki(self) -> bool:
        success = False
        # 进入候补设置
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_BACKUP_PAGE_CHECK):
                break

            if self.appear(self.I_BACKUP_CONFIG):
                self.click(self.I_BACKUP_CONFIG)

        # 清空狗粮
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_BACKUP_PUT):
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

        while total < 5:
            self.wait_and_shot(1)

            if self.appear(self.I_M_RED):
                self.long_click(self.I_M_RED)
                total += 1

            if self.appear(self.I_M_WHITE):
                self.long_click(self.I_M_WHITE)
                total += 1

            self.swipe(self.S_SHIKI_TO_LEFT)

    def left_check(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_EXP_BATTLE) or self.appear(self.I_EXP_BOSS):
                break
            self.swipe(self.S_EXP_TO_LEFT)

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

    def get_chapter_reward(self):
        logger.info("Trying to find chapter reward...")
        # 章节通关奖励，好像最多只有三个
        found = False
        time.sleep(1)
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_EXP) or self.appear(self.I_C_EXP_MODAL) or self.appear(self.I_EXP_YAOQI):
                break

            if self.wait_until_click(self.I_EXP_CHAP_REWARD):
                if self.appear(self.I_GAIN_REWARD):
                    self.random_click_right()
                    found = True

        if found:
            logger.info("Got all chapter reward.")
        return found

    def check_ticket(self):
        if not self.exp_config.scroll_mode.scroll_mode_enable:
            return

        image = self.screenshot()
        count, total = self.O_EXP_VIEW_TICKET_COUNT.digit_counter(image)

        # 判断突破票数量
        if count is None:
            return

        if count < self.exp_config.scroll_mode.ticket_threshold:
            if not self.is_buff_on:
                self.open_config_buff()
                self.is_buff_on = True
            return
        else:
            if self.is_buff_on:
                self.close_config_buff()

        self.activate_realm_raid()

    def activate_realm_raid(self):
        # 设置下次执行行时间
        logger.info("|| RealmRaid and Exploration set_next_run ||")
        hr, min, sec = self.exp_config.scroll_mode.scrolls_cd.split(":")
        next_run = datetime.now() + timedelta(hours=int(hr),
                                              minutes=int(min),
                                              seconds=int(sec))
        logger.warning(f"next run time: {next_run}")
        self.set_next_run(task='Exploration', success=False,
                          finish=False, target_time=next_run)
        self.set_next_run(task='RealmRaid', success=False,
                          finish=False, target_time=datetime.now())

        raise TaskEnd(self.name)

    def open_config_buff(self):
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
