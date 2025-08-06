import sys
from module.base.logger import logger
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.config.enums import ChapterHardness, Chapters
from tasks.exploration.exp_base import ExpBase
from tasks.general.page import page_exp, page_main, page_realm_raid

from datetime import datetime, timedelta
import time

class TaskScript(ExpBase):
    init_battle = True
    init_hardness = True

    def run(self):
        self.exp_config = self.config.model.exploration

        # 进入探索页面
        if not self.check_page_appear(page_exp):
            self.goto(page_exp)

        # 判断是否开启绘卷模式
        scroll_mode = self.exp_config.scroll_mode
        exp_count = self.exp_config.exploration_config.count_max

        self.check_ticket()

        count = 0
        while count < exp_count:
            # 检查票数
            self.check_ticket()

            self.enter_chapter()
            self.class_logger(self.name,
                              f"======== Round {count + 1} Exp Started =========")
            # 进入章节战斗
            self.pre_chapter_battle()
            self.chapter_battle()
            self.after_chapter_battle()

            count += 1

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

        ss_config = self.exp_config.switch_soul_config
        ss_enable = ss_config.enable
        if ss_enable:
            self.run_switch_souls(
                self.I_SHIKI_BOOK_ENT, ss_config.switch_group_team, self.I_EXP_C_CHAPTER)

        self.toggle_exp_team_lock(
            self.exp_config.exploration_config.lock_team_enable)

        self.init_battle = False

    def after_chapter_battle(self):
        # 检查章节奖励
        self.get_chapter_reward()

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

    def find_assigned_chapter(self, pick_chapter):
        chapter_list = [chapter.value for chapter in Chapters]
        chapter_set = set(chapter_list)  # For faster lookup
        swipe_count = 0
        swipe_action = self.S_EXP_CHAPTER_UP

        # 找到预设章节位置，如果不在当前页面，则滑动
        while 1:
            image = self.wait_and_shot()
            results = self.O_EXP_CHAPTER.detect_and_ocr(image)
            texts = [result.ocr_text for result in results]
            logger.warning(f"[EXP] ocr results: {texts}")
            is_chapter_visible = pick_chapter in texts

            if is_chapter_visible:
                self.O_EXP_CHAPTER.keyword = pick_chapter
                break

            if swipe_count > 10:
                raise RequestHumanTakeover("Unable to find target chapter")

            # 计算应该往上还是往下滑
            found_chapter = next(
                (text for text in texts if text in chapter_set), None)

            if found_chapter:
                cur_pos = chapter_list.index(found_chapter)
                target_pos = chapter_list.index(pick_chapter)

                if target_pos < cur_pos:
                    swipe_action = self.S_EXP_CHAPTER_DOWN
                    logger.debug(
                        f"current pos: {cur_pos}, target pos: {target_pos}. Going to swipe down.")
                else:
                    swipe_action = self.S_EXP_CHAPTER_UP
                    logger.debug(
                        f"current pos: {cur_pos}, target pos: {target_pos}. Going to swipe up.")

            self.swipe(swipe_action)
            swipe_count += 1
            time.sleep(0.5)

            self.O_EXP_CHAPTER.keyword = pick_chapter

        # 找到预设章节
        self.find_ocr_target(self.O_EXP_CHAPTER)

    def enter_chapter(self):
        pick_chapter = self.exp_config.exploration_config.chapter
        if pick_chapter is Chapters.CHAPTER_28:
            self.enter_chap_28()
            return

        # 如果当前章节不是预设章节，则找到预设章节
        if self.O_EXP_CHAPTER.keyword != pick_chapter:
            self.find_assigned_chapter(pick_chapter)
            self.init_hardness = True
            self.select_chapter_hardness()

        self.class_logger(self.name, f"Entering chapter {pick_chapter}")
        # 进入预设章节
        while 1:
            self.wait_and_shot(0.6)
            if self.appear(self.I_EXP_BUTTON, 0.98):
                break

            self.ocr_click(self.O_EXP_CHAPTER)

        self.click_static_target(self.I_EXP_BUTTON, 0.97, delay=1)

    def select_chapter_hardness(self):
        if not self.init_hardness:
            return

        hardness = self.exp_config.exploration_config.chapter_hardness
        self.class_logger(self.name, f"Selected hardness: {hardness}")
        if hardness == ChapterHardness.RANDOM:
            return

        if hardness == ChapterHardness.HARD:
            self.click(self.C_EXP_HARD)
        else:
            self.click(self.C_EXP_REGULAR)
        self.init_hardness = False

    def enter_chap_28(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_EXP_CHAP_28, 0.98):
                break
            self.swipe(self.S_EXP_CHAPTER_UP)

        self.class_logger(self.name, "Entering chapter 28")
        if self.click_static_target(self.I_EXP_CHAP_28):
            self.select_chapter_hardness()
            self.click_static_target(self.I_EXP_BUTTON, 0.97, delay=1)

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
        found = False
        time.sleep(1)
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_EXP_C_CHAPTER, 0.95):
                break

            if self.appear(self.I_GAIN_REWARD):
                self.random_click_right()
                found = True

            if self.appear(self.I_EXP_CHAP_REWARD):
                self.click(self.I_EXP_CHAP_REWARD)

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
