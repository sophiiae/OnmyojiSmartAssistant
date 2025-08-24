from functools import cached_property
import random
import time
from module.base.logger import logger
from module.base.exception import TaskEnd
from module.image_processing.rule_click import RuleClick
from module.image_processing.rule_image import RuleImage
from tasks.components.battle.battle import Battle
from tasks.rifts_shadows.assets import RiftsShadowsAssets
from tasks.components.page.page import page_guild, page_main


class TaskScript(RiftsShadowsAssets, Battle):
    name = "RiftsShadows"

    def run(self):
        self.rs_config = self.config.model.rifts_shadows.rifts_shadows_config
        self.shadows = list(self.shadow_clicks.keys())
        random.shuffle(self.shadows)

        # 进入庭院页面
        if not self.check_page_appear(page_guild):
            self.goto(page_guild)

        success = True

        if self.wait_until_appear(self.I_RS_GUILD_ENT, 300):
            self.run_rs()
        else:
            success = False

        self.set_next_run(self.name, finish=False, success=success)
        self.goto(page_main)
        raise TaskEnd(self.name)

    @cached_property
    def shadow_clicks(self):
        return {
            # [狭间主页点击区域， 战报小图像]
            1: [self.C_DARK_DIVINE_DRAGON_SHADOW, self.I_T_DDD],
            2: [self.C_DARK_HAKUZOUSU_SHADOW, self.I_T_DH],
            3: [self.C_DARK_PEACOCK_SHADOW, self.I_T_DP],
            4: [self.C_DARK_BLACK_PANTHER_SHADOW, self.I_T_DBP]
        }

    @property
    def battle_map(self):
        return {
            1: [self.I_T_LEADER],
            2: [self.I_T_DEPUTY_L, self.I_T_DEPUTY_R],
            3: [self.I_T_ELITE_L, self.I_T_ELITE_M, self.I_T_ELITE_R]
        }

    @cached_property
    def battle_map_click(self):
        return {
            1: [self.C_R_LEADER],
            2: [self.C_R_DEPUTY_L, self.C_R_DEPUTY_R],
            3: [self.C_R_ELITE_L, self.C_R_ELITE_M, self.C_R_ELITE_R]
        }

    @property
    def attack_counts(self):
        return {1: 2, 2: 4, 3: 6}  # 首领：2，副将：4，精英：6

    @cached_property
    def mini_map_attack_order(self):
        return [
            [self.I_RS_DEMON_DEPUTY_L, self.I_RS_DEMON_DEPUTY_R],
            [self.I_RS_DEMON_ELITE_L, self.I_RS_DEMON_ELITE_M, self.I_RS_DEMON_ELITE_R]
        ]

    def enter_rs_page(self):
        # 进入狭间暗域
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_RIFTS_SHADOW):
                break

            self.appear_then_click(self.I_RS_GUILD_ENT)

    def run_rs(self):
        leader_bt = self.rs_config.leader_battle_time

        self.enter_rs_page()

        key = self.shadows[0]
        self.enter_shadow(self.shadow_clicks[key][0])  # 第一个暗域

        # 打第一个首领
        self.class_logger(self.name, "Attacking 1st leader")
        if self.enter_from_mini_map(self.I_RS_DEMON_LEADER):
            self.start_battle(leader_bt)
        self.attack_rest()

        self.shadows.remove(key)

        # 打第二个首领
        self.class_logger(self.name, "Attacking 2nd leader")
        target_shadow = self.switch_shadow_battle(1)
        if target_shadow:
            key = target_shadow
            self.start_battle(leader_bt)
            self.attack_rest()

    def exit_rs(self):
        while 1:
            self.wait_and_shot()
            if self.check_page_appear(page_guild):
                break

            self.appear_then_click(self.I_RS_EXIT)

    def attack_rest(self):
        deputy_bt = self.rs_config.deputy_battle_time
        elite_bt = self.rs_config.elite_battle_time
        # 打剩下的
        self.class_logger(self.name, "Attacking rest.")
        for index, demon_list in enumerate(self.mini_map_attack_order):
            battle_time = deputy_bt if index == 0 else elite_bt
            for demon in demon_list:
                if self.enter_from_mini_map(demon):
                    self.start_battle(battle_time)

    def enter_shadow(self, target_shadow: RuleImage | RuleClick):
        # 从狭间主页进入
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_RS_SHIKI_BOOK_ENT, 0.95):
                break

            self.click(target_shadow)

        # 更换御魂
        ss_config = self.config.model.rifts_shadows.switch_soul_config
        ss_enable = ss_config.enable

        if ss_enable:
            self.run_switch_souls(self.I_RS_SHIKI_BOOK_ENT,
                                  ss_config.switch_group_team,
                                  self.I_RS_SHIKI_BOOK_ENT)

    def start_battle(self, battle_time):
        # 挑战
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_BATTLE_READY):
                break
            self.appear_then_click(self.I_RS_BATTLE)

        # 开始战斗
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_BATTLE_READY):
                self.class_logger(
                    self.name, f"Going to wait for {battle_time} seconds.")
                time.sleep(battle_time)
                break

            self.appear_then_click(self.I_BATTLE_READY)

        self.exit_battle(self.I_RS_SHIKI_BOOK_ENT)

    def enter_from_mini_map(self, target):
        # 放大小地图
        retry = 0
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_RS_HEAD_FOR):
                break

            if retry > 3:
                return False

            if self.appear_then_click(target, 0.96):
                retry += 1

            self.click(self.C_RS_MINI_MAP)

        self.wait_until_appear(self.I_RS_BATTLE, 20)
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_RS_BATTLE):
                break

            self.appear_then_click(self.I_RS_HEAD_FOR)

    def switch_shadow_battle(self, demon_type: int):
        # 打开战报
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_RS_DEMON_DIST, 0.95):
                break

            self.appear_then_click(self.I_RS_BATTLE_REPORT)

        for shadow in self.shadows:
            t_img = self.shadow_clicks[shadow][1]
            self.click(t_img)
            index = self.get_demon_index(demon_type)
            if index:
                self.go_and_attack(self.battle_map_click[demon_type][index])
                return shadow

        logger.error(
            f"Not able to get demon type [{demon_type}] in rest shadows.")
        return None

    def go_and_attack(self, target):
        self.class_logger(self.name, f"Go and attack target {target.name}")
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_RS_HEAD_FOR):
                break

            self.click(target)

        # 前往
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_RS_HEAD_FOR):
                break

            if self.appear_then_click(self.I_B_CONFIRM_WIDE, 0.95):
                continue

            self.appear_then_click(self.I_RS_HEAD_FOR)

        self.wait_until_appear(self.I_RS_BATTLE, 10)

    def get_demon_index(self, type: int):
        image = self.screenshot()

        parts = self.battle_map[type]
        for idx, part in enumerate(parts):
            cropped = part.crop(image)
            if self.I_DEMON_LIFE.match_target(cropped, threshold=0.95, cropped=True):
                return idx

        logger.error("Not able to get demo index.")
        return None
