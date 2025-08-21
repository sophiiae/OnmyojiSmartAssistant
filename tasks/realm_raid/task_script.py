from datetime import datetime, timedelta
from functools import cached_property
import random
import time
from module.base.logger import logger
from module.base.exception import TaskEnd
from module.image_processing.rule_image import RuleImage
from tasks.realm_raid.assets import RealmRaidAssets
from tasks.components.page.page import page_realm_raid, page_main, page_exp
from module.base.exception import RequestHumanTakeover
from tasks.components.battle.battle import Battle

class TaskScript(RealmRaidAssets, Battle):
    reverse: bool = False
    name = "RealmRaid"

    def run(self):
        self.rr_config = self.config.model.realm_raid.raid_config

        if not self.check_page_appear(page_realm_raid):
            if self.check_page_appear(page_exp):
                self.goto(page_realm_raid, page_exp)
            else:
                self.goto(page_realm_raid)

        enough_ticket = self.check_ticket()
        enable_guild = self.rr_config.enable_guild_realm_raid

        # 检查票数
        if not enough_ticket and not enable_guild:
            self.goto(page_main)
            self.set_next_run(task='RealmRaid', success=False, finish=False)
            raise TaskEnd(self.name)

        # 更换御魂
        ss_config = self.config.model.realm_raid.switch_soul_config
        ss_enable = ss_config.enable

        if ss_enable:
            self.run_switch_souls(self.I_RR_SHIKI_BOOK_ENT,
                                  ss_config.switch_group_team,
                                  self.I_REALM_RAID_HEADER)

        success = True
        # 个人突破
        if enough_ticket:
            success = self.start_individual_raid(enough_ticket)

        # 寮突破
        if enable_guild:
            success = self.start_guild_raid()

        exp_enabled = self.config.model.exploration.scheduler.enable
        scroll_mode_enabled = self.config.model.exploration.scroll_mode.scroll_mode_enable

        # 绘卷模式去探索页面，减少页面跳转
        if exp_enabled and scroll_mode_enabled:
            self.goto(page_exp, page_realm_raid)
        else:
            self.goto(page_main, page_realm_raid)

        self.set_next_run(task='RealmRaid', success=success, finish=True)
        raise TaskEnd(self.name)

    def start_individual_raid(self, enough_ticket) -> bool:
        # 进入个人突破
        while 1:
            self.screenshot()
            if self.appear(self.I_RR_RANK_ICON):
                break

            self.click(self.C_INDIVIDUAL_RAID)

        success = True
        while enough_ticket:
            success = True
            # 如果最低挑战等级高于57，就降级处理
            if not self.downgrade():
                success = False
            else:
                attack_list = self.get_viable_partition_indexes()

                # 开始一轮战斗
                success = self.start_battle(attack_list)

            # 根据战斗结果判断是否刷新
            if success:
                self.reverse = not self.reverse
            else:
                self.click_refresh()

            enough_ticket = self.check_ticket()
        self.class_logger(
            self.name, "Completed all battles, no enough ticket for next round. ")
        return success

    def start_guild_raid(self):
        # 进入寮突破
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_GUILD_RAID_CLOSE, 0.95):
                self.class_logger(self.name, "Guild raid hasn't opened yet.")
                return True

            if self.appear(self.I_RR_GUID_PROGRESS):
                break

            self.click(self.C_GUILD_RAID)

        # 寮已全部攻破
        if self.appear(self.I_RR_GUILD_CONQUER):
            return True

        image = self.screenshot()
        count, total = self.O_GUILD_RAID_TICKET.digit_counter(image)
        self.class_logger(self.name, f"Got {count} tickets for guild raid. ")
        if count == 0:
            return True

        indexes = self.find_guild_attack_indexes()
        attack_index = indexes.pop(0)
        while count:
            if not indexes:
                indexes = self.find_guild_attack_indexes()
                continue

            self.enter_guild_battle(self.guild_partitions[attack_index])
            if self.run_easy_battle(self.I_RR_GUID_PROGRESS, self.I_REALM_RAID_FAILED):
                count -= 1
            else:
                attack_index = indexes.pop(0)

        return count == 0

    def find_guild_attack_indexes(self) -> list[int]:
        indexes = self.get_guild_partition_indexes()
        while not indexes:
            self.swipe(self.S_RAID_DOWN, duration=600)
            time.sleep(1)
            indexes = self.get_guild_partition_indexes()

        return indexes

    def enter_guild_battle(self, target: RuleImage):
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_RR_GUID_PROGRESS):
                break

            if self.appear_then_click(self.I_RAID_ATTACK, 0.96, 0.3):
                continue

            x, y = target.roi_center_random()
            self.device.click(x, y)

    def start_battle(self, attack_list: list[int]) -> bool:
        # 锁定队伍
        self.toggle_realm_team_lock()

        if not attack_list:
            return False

        # 开始战斗
        success = True
        attack_index = 1
        self.class_logger(self.name, f"----- attack order: {attack_list}")
        image = self.screenshot()
        level = self.O_RAID_PARTITION_9_LV.digit(image)
        skip_quit = level < 57

        while len(attack_list) > 0:
            # 下一个挑战目标
            attack_index = attack_list.pop(0)

            time.sleep(1)
            # 最后一个退4次再打， 卡57
            self.class_logger(
                self.name, f"----- Attacking index {attack_index}.")
            if attack_index == 9 and not self.reverse and not skip_quit:
                self.quit_and_fight(attack_index)

            attack_count = 0
            while attack_count < 5:
                self.enter_battle(self.partitions[attack_index])
                if not self.run_easy_battle(self.I_REALM_RAID_HEADER, self.I_REALM_RAID_FAILED):
                    logger.warning(f"Failed to attack index {attack_index}")
                    success = False
                    attack_count += 1
                    continue
                else:
                    success = True
                    break

        self.wait_and_shot()
        if self.appear(self.I_REWARD):
            self.get_reward()

        return success

    def enter_battle(self, target):
        while 1:
            self.wait_and_shot(1)
            if not self.appear(self.I_RR_RANK_ICON):
                break

            if self.appear(self.I_RAID_ATTACK_MODAL, 0.97):
                if self.appear_then_click(self.I_RAID_ATTACK):
                    continue

            if self.click(target):
                continue

    def get_viable_partition_indexes(self):
        image = self.screenshot()
        indexes = []
        for idx, part in self.partitions.items():
            cropped = part.crop(image)
            if self.I_RAID_BEAT.match_target(cropped, threshold=0.95, cropped=True) or self.I_RAID_LOSE.match_target(cropped, threshold=0.95, cropped=True):
                continue

            indexes.append(idx)

        if len(indexes) == len(self.partitions) and self.reverse:
            indexes.reverse()
        else:
            self.reverse = False

        self.class_logger(self.name, f"attack list: {indexes}")
        return indexes

    def get_guild_partition_indexes(self):
        image = self.screenshot()
        indexes = []
        for idx, part in self.guild_partitions.items():
            cropped = part.crop(image)
            if self.I_RAID_BEAT.match_target(cropped, threshold=0.95, cropped=True) or self.I_RR_GUILD_LOSE.match_target(cropped, cropped=True):
                continue
            indexes.append(idx)

        self.class_logger(self.name, f"attack list: {indexes}")
        return indexes

    @cached_property
    def partitions(self):
        return {
            1: self.I_REALM_PARTITION_1,
            2: self.I_REALM_PARTITION_2,
            3: self.I_REALM_PARTITION_3,
            4: self.I_REALM_PARTITION_4,
            5: self.I_REALM_PARTITION_5,
            6: self.I_REALM_PARTITION_6,
            7: self.I_REALM_PARTITION_7,
            8: self.I_REALM_PARTITION_8,
            9: self.I_REALM_PARTITION_9
        }

    @cached_property
    def guild_partitions(self):
        return {
            1: self.I_GUILD_PARTITION_1,
            2: self.I_GUILD_PARTITION_2,
            3: self.I_GUILD_PARTITION_3,
            4: self.I_GUILD_PARTITION_4,
            5: self.I_GUILD_PARTITION_5,
            6: self.I_GUILD_PARTITION_6,
        }

    def quit_and_fight(self, index, quit_count=4):
        self.class_logger(
            self.name, f"Starting quit and fight for {quit_count} times.")

        self.toggle_realm_team_lock(False)
        count = 1
        while count <= quit_count:
            self.click(self.partitions[index])
            if not self.wait_until_click(self.I_RAID_ATTACK, 3):
                logger.error("Not able to enter battle")
                raise RequestHumanTakeover
            self.class_logger(
                self.name, f"========= quit and fight count: {count}")
            time.sleep(0.5)

            self.run_battle_quit()
            count += 1

        self.toggle_realm_team_lock()

    def is_downgrad_required(self):
        image = self.screenshot()
        level = self.O_RAID_PARTITION_1_LV.digit(image)
        downgrad_required = False

        if level > 57:
            level_3 = self.O_RAID_PARTITION_3_LV.digit(image)
            if level_3 > 57:
                level_9 = self.O_RAID_PARTITION_9_LV.digit(image)
                if level_9 > 57:
                    self.class_logger(self.name,
                                      f"----- level_1: {level}, level_3: {level_3}, level_9: {level_9}")
                    downgrad_required = True

        return downgrad_required

    def downgrade(self) -> bool:
        self.screenshot()
        if not self.wait_until_appear(self.I_REALM_RAID_HEADER, 2):
            return False

        downgrad_required = self.is_downgrad_required()
        retry = 5
        while downgrad_required:
            # 不锁定退得快点
            self.toggle_realm_team_lock(False)
            indexes = self.get_viable_partition_indexes()
            for idx in indexes:
                self.class_logger(
                    self.name, f"** enter and quit for partition {idx}")
                self.click(self.partitions[idx])

                if self.wait_until_click(self.I_RAID_ATTACK):
                    self.run_battle_quit()
                else:
                    logger.warning(f"No attack button found for {idx}")
                time.sleep(1)

            # 都退完了，刷新
            if not self.click_refresh():
                return False
            time.sleep(0.3)

            # 更新现在的最低等级
            downgrad_required = self.is_downgrad_required()
            retry -= 1

        if retry < 0:
            logger.critical(f"Run out of retry for downgrade")
            return False

        self.class_logger(self.name, f"Current level meets requirement.")
        return True

    def click_refresh(self) -> bool:
        """
        检查是否出现了刷新的按钮
        如果可以刷新就刷新, 返回True
        如果在CD中, 就返回False
        :return:
        """
        self.wait_and_shot()
        if self.appear_then_click(self.I_RAID_REFRESH, delay=0.5):
            if self.wait_until_click(self.I_BATTLE_FIGHT_AGAIN_CONFIRM, 2):
                return True

        logger.critical("No refresh button found")
        target_time = datetime.now() + timedelta(minutes=5)
        self.set_next_run(self.name, success=True,
                          finish=True, target_time=target_time)
        raise TaskEnd(
            self.name, f"Waiting for refresh button to be enabled. {self.name}")

    def check_ticket(self):
        tickets_required = self.rr_config.tickets_required
        time.sleep(0.2)
        if tickets_required < 0 or tickets_required > 30:
            logger.warning(f'It is not a valid base: {tickets_required}')
            tickets_required = 0

        image = self.screenshot()
        count, total = self.O_RAID_TICKET.digit_counter(image)
        if total == 0:
            # 处理奖励之后，重新识别票数
            self.get_rr_reward()
            time.sleep(1)
            image = self.screenshot()
            count, total = self.O_RAID_TICKET.digit_counter(image)
        if count < tickets_required:
            logger.warning(f'Execute raid failed, ticket is not enough')
            return False
        return True

    def get_rr_reward(self):
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_REWARD):
                break

            if self.appear(self.I_REWARD):
                self.random_click_right()
                self.class_logger(self.name, "Got realm raid fight reward")
                continue

    def toggle_realm_team_lock(self, lock: bool = True):
        is_in_activity = self.appear(self.I_RAID_TEAM_LOCK_2, 0.95) or self.appear(
            self.I_RAID_TEAM_UNLOCK_2, 0.95)
        if is_in_activity:
            return self.toggle_team_lock(self.I_RAID_TEAM_LOCK_2, self.I_RAID_TEAM_UNLOCK_2, lock)

        return self.toggle_team_lock(self.I_RAID_TEAM_LOCK, self.I_RAID_TEAM_UNLOCK, lock)
