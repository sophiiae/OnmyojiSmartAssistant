import sys
from module.base.logger import logger
from module.base.exception import RequestHumanTakeover, TaskEnd
from tasks.exploration.exp_base import ExpBase
from tasks.general.page import page_exp, page_main, page_realm_raid

from datetime import datetime, timedelta
import time

class TaskScript(ExpBase):
    init_battle = True

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

            self.class_logger(self.name,
                              f"======== Round {count + 1} Exp Started =========")
            # 进入章节战斗
            self.pre_chapter_battle()
            self.chapter_battle()
            self.after_chapter_battle()

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

    def pre_chapter_battle(self):
        # ************************* 进入设置并操作 *******************
        if not self.wait_until_appear(self.I_EXP_C_CHAPTER, 2):
            logger.warning(
                "*Exp* Not inside chapter or battle finished.")
            raise RequestHumanTakeover

        if not self.init_battle:
            return

        ss_config = self.config.model.exploration.switch_soul_config
        ss_enable = ss_config.enable
        if ss_enable:
            self.run_switch_souls(
                self.I_SHIKI_BOOK_ENT, ss_config.switch_group_team, self.I_EXP_C_CHAPTER)
            self.init_battle = False

    def after_chapter_battle(self):
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

    def chapter_battle(self):
        # 进入战斗环节
        self.class_logger(self.name, "Start battle...")
        swipe_count = 0
        stuck_count = 0
        while 1:
            # 如果一直卡住，检查候补狗粮
            if stuck_count > 5:
                self.check_auto_rotate()

            self.wait_and_shot()

            # BOSS 挑战
            if self.appear(self.I_EXP_BOSS):
                self.click_moving_target(self.I_EXP_BOSS, self.I_EXP_C_CHAPTER)

                if self.run_easy_battle(self.I_EXP_C_CHAPTER):
                    self.get_chapter_reward()
                    break
                else:
                    stuck_count += 1

            # 普通怪挑战
            if self.appear(self.I_EXP_BATTLE):
                self.click_moving_target(
                    self.I_EXP_BATTLE, self.I_EXP_C_CHAPTER)
                if self.run_easy_battle(self.I_EXP_C_CHAPTER):
                    swipe_count = 0
                    stuck_count = 0
                else:
                    stuck_count += 1
                continue

            self.swipe(self.S_EXP_TO_RIGHT)
            swipe_count += 1
            if swipe_count > 7:
                self.left_check()
                swipe_count = 0
            time.sleep(0.3)

        time.sleep(1)

    def check_auto_rotate(self):
        if not self.turn_on_auto_rotate():
            auto_backup = self.exp_config.exploration_config.auto_backup
            auto_soul_clear = self.exp_config.exploration_config.auto_soul_clear

            if not auto_backup and not auto_soul_clear:
                self.exit_chapter()

            if auto_backup:
                self.auto_backup()
            if auto_soul_clear:
                self.soul_clear()

    def turn_on_auto_rotate(self) -> bool:
        # 自动轮换功能打开
        retry = 0
        while 1:
            self.wait_and_shot()

            # 自动轮换开着 则跳过
            if self.appear(self.I_AUTO_ROTATE_ON):
                break

            if retry > 3:
                logger.warning("Running out of backup!")
                return False

            # 自动轮换关着 则打开
            if self.appear_then_click(self.I_AUTO_ROTATE_OFF):
                retry += 1
                continue

        return True

    def left_check(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_EXP_BATTLE) or self.appear(self.I_EXP_BOSS):
                break
            self.swipe(self.S_EXP_TO_LEFT)

    def get_chapter_reward(self):
        self.class_logger(self.name, "Trying to find chapter reward...")
        # 章节通关奖励，好像最多只有三个
        found = False
        time.sleep(1)
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_EXP_C_CHAPTER, 0.95):
                break

            if self.wait_until_click(self.I_EXP_CHAP_REWARD):
                if self.appear(self.I_GAIN_REWARD):
                    self.random_click_right()
                    found = True

        if found:
            self.class_logger(self.name, "Got all chapter reward.")
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
        self.class_logger(
            self.name, "|| RealmRaid and Exploration set_next_run ||")
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
