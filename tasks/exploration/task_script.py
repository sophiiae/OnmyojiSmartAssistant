
import sys
from module.base.logger import logger
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.control.config.enums import BuffClass
from tasks.battle.battle import Battle
from tasks.exploration.assets import ExplorationAssets as EA
from tasks.general.page import Page, page_exp, page_main
from trifle_fairy.config.config import Config

from datetime import datetime, timedelta
import time

class TaskScript(EA, Battle):
    name = "Exploration"
    scroll_mode_enable = False
    ticket_threshold = 22
    scrolls_cd = "0:30:00"
    buff = []

    def _get_config(self):
        ticket_threshold = self.config.model.deep_get(
            self.exp_config, 'ticket_threshold')
        if ticket_threshold:
            self.ticket_threshold = ticket_threshold
        scrolls_cd = self.config.model.deep_get(self.exp_config, 'scrolls_cd')
        if scrolls_cd:
            self.scrolls_cd = scrolls_cd
        scroll_mode_enable = self.config.model.deep_get(
            self.exp_config, 'scroll_mode_enable')
        if scroll_mode_enable is not None:
            self.scroll_mode_enable = scroll_mode_enable
        if self.config.model.deep_get(
                self.exp_config, 'buff_gold_50'):
            self.buff.append('buff_gold_50')
        if self.config.model.deep_get(
                self.exp_config, 'buff_gold_100'):
            self.buff.append('buff_gold_50')
        if self.config.model.deep_get(
                self.exp_config, 'buff_exp_50'):
            self.buff.append('buff_gold_50')
        if self.config.model.deep_get(
                self.exp_config, 'buff_exp_100'):
            self.buff.append('buff_gold_50')

    def run(self):
        self.exp_config = self.config.model.exploration
        self._get_config()
        # 进入探索页面
        if not self.check_page_appear(page_exp):
            self.goto(page_exp)

        # 判断是否开启绘卷模式
        if self.scroll_mode_enable:
            exp_count = 50
        else:
            max_count = self.config.model.deep_get(
                self.exp_config, 'max_count')
            exp_count = max_count if max_count else 0

        self.open_config_buff()
        count = 0
        while exp_count > 0 and count < exp_count:
            # 检查票数
            self.check_ticket()

            if self.click_static_target(self.I_EXP_CHAPTER_28):
                self.click_static_target(self.I_EXP_BUTTON)

            logger.info(f"======== Round {count + 1} Exp Started =========")
            # 进入章节战斗
            self.battle_process()

            # 如果回到了探索界面 -> 检查宝箱
            if self.wait_until_appear(self.I_C_EXP, 2):
                self.check_treasure_box()
            else:
                # 出现章节入口 -> 没有发现 -> 关闭
                self.click_static_target(self.I_EXP_CHAPTER_DISMISS_ICON)

            count += 1

        self.close_config_buff()
        self.goto(page_main, page_exp)

        raise TaskEnd(self.name)

    def check_treasure_box(self):
        while 1:
            time.sleep(0.3)
            self.screenshot()
            if not self.appear(self.I_EXP_TREASURE_BOX_MAP, 0.95):
                break

            if self.appear(self.I_EXP_TREASURE_BOX_MAP, 0.95):
                self.click(self.I_EXP_TREASURE_BOX_MAP)

                got_reward = self.wait_until_appear(
                    self.I_REWARD, 3)

                # 如果检测偏差，是妖气封印，就关闭退出
                if self.appear(self.I_EXP_YAOQI):
                    self.click(self.I_EXP_YAOQI_CLOSE)
                    break

                if got_reward:   # 领取宝箱物品
                    time.sleep(0.7)
                    self.random_click_right()

    def battle_process(self):
        # ************************* 进入设置并操作 *******************
        # 自动轮换功能打开
        while 1:
            self.screenshot()
            # 自动轮换开着 则跳过
            if self.appear(self.I_AUTO_ROTATE_ON):
                break
            # 自动轮换关着 则打开
            if self.appear_then_click(self.I_AUTO_ROTATE_OFF):
                if self.appear(self.I_AUTO_ROTATE_ON):
                    break

        # 进入战斗环节
        logger.info("Start battle...")
        while 1:
            if not self.wait_until_appear(self.I_EXP_C_CHAPTER, 1.5):
                logger.warning(
                    "***** Not inside chapter or battle finished.")
                raise RequestHumanTakeover

            # BOSS 挑战
            if self.appear(self.I_EXP_BOSS):
                time.sleep(0.6)
                self.appear_then_click(self.I_EXP_BOSS)

                if self.run_battle():
                    self.get_chapter_reward()
                    break

            # 普通怪挑战
            if self.appear_then_click(self.I_EXP_BATTLE):
                self.run_battle()

            else:
                self.swipe(self.S_EXP_TO_RIGHT)

            time.sleep(0.3)

        time.sleep(1)

    def get_chapter_reward(self):
        logger.info("Trying to find chapter reward...")
        # 章节通关奖励，好像最多只有三个
        found = False
        time.sleep(1)
        while 1:
            time.sleep(0.3)
            self.screenshot()
            if self.appear(self.I_C_EXP) or self.appear(self.I_C_EXP_MODAL):
                break

            if self.click_static_target(self.I_EXP_CHAP_REWARD):
                if self.appear(self.I_GAIN_REWARD):
                    self.random_click_right()
                    found = True

        if found:
            logger.info("Got all chapter reward.")
        return found

    def check_ticket(self):
        if not self.scroll_mode_enable:
            return

        image = self.screenshot()
        count, total = self.O_EXP_VIEW_TICKET_COUNT.digit_counter(image)

        # 判断突破票数量
        if count is None or count < self.ticket_threshold:
            return

        self.activate_realm_raid()

    def activate_realm_raid(self):
        # 设置下次执行行时间
        logger.info("|| RealmRaid and Exploration set_next_run ||")
        hr, min, sec = self.scrolls_cd.split(":")
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
        if 'buff_gold_50' in self.buff:
            buff.append(BuffClass.GOLD_50)
        if 'buff_gold_100' in self.buff:
            buff.append(BuffClass.GOLD_100)
        if 'buff_exp_50' in self.buff:
            buff.append(BuffClass.EXP_50)
        if 'buff_exp_100' in self.buff:
            buff.append(BuffClass.EXP_100)

        return self.check_buff(buff, page_exp)

    def close_config_buff(self):
        buff = []
        if 'buff_gold_50' in self.buff:
            buff.append(BuffClass.GOLD_50_CLOSE)
        if 'buff_gold_100' in self.buff:
            buff.append(BuffClass.GOLD_100_CLOSE)
        if 'buff_exp_50' in self.buff:
            buff.append(BuffClass.EXP_50_CLOSE)
        if 'buff_exp_100' in self.buff:
            buff.append(BuffClass.EXP_100_CLOSE)

        return self.check_buff(buff, page_exp)
