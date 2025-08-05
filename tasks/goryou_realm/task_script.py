from functools import cached_property
import random
from module.base.logger import logger
from tasks.battle.battle import Battle
from tasks.general.page import page_main, page_goryou
from tasks.goryou_realm.assets import GoryouRealmAssets as GR
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.config.enums import GoryouClass, GoryouLevel

class TaskScript(Battle, GR):
    name = 'Goryou Realm'

    def run(self):
        self.gr_config = self.config.model.goryou_realm.goryou_config
        self.gr_class = self.gr_config.goryou_class

        # 进入御灵页面
        if not self.appear(self.I_GR_FIGHT_CHECK) and not self.appear(self.I_GR_CHECK):
            self.goto(page_goryou)

        # 选择御灵
        if self.appear(self.I_GR_CHECK):
            if not self.choose_class():
                self.set_next_run(task='GoryouRealm',
                                  finish=True, success=False)
                raise TaskEnd("No Goryou class open")

        # 选择御灵层数
        self.choose_level()

        # 更换御魂
        ss_config = self.config.model.goryou_realm.switch_soul_config
        ss_enable = ss_config.enable
        if ss_enable:
            self.run_switch_souls(
                self.I_GR_SHIKI_BOOK, ss_config.switch_group_team, self.I_GR_FIGHT_CHECK)

        # 开始战斗
        self.start_battle()

        self.set_next_run(task='GoryouRealm', finish=True, success=True)
        self.goto(page_main, page_goryou)

        raise TaskEnd(self.name)

    @cached_property
    def open_class_match(self):
        return {
            GoryouClass.Dark_Divine_Dragon: self.I_GR_DDD_OPEN,
            GoryouClass.Dark_Hakuzousu: self.I_GR_DH_OPEN,
            GoryouClass.Dark_Black_Panther: self.I_GR_DBP_OPEN,
            GoryouClass.Dark_Peacock: self.I_GR_DP_OPEN
        }

    def get_goryou_class(self, pick: GoryouClass):
        self.screenshot()
        if pick is not GoryouClass.RANDOM:
            # 如果选择的御灵开放就直接返回
            if self.appear(self.open_class_match[pick]):
                self.class_logger(self.name, f"Choose assigned Goryou: {pick}")
                return pick

        # 查找开放的御灵
        open_classes = []
        for k, v in self.open_class_match.items():
            if self.appear(v, 0.985):
                open_classes.append(k)

        # 如果都不开放
        if not open_classes:
            logger.warning("No Goryou open.")
            return None

        self.class_logger(
            self.name, f"Current open goryou classes: {open_classes}")

        # 随机御灵
        index = random.randint(0, len(open_classes) - 1)
        chosen_class = open_classes[index]
        self.class_logger(self.name, f"Choose random Goryou: {chosen_class}")
        return chosen_class

    @cached_property
    def goryou_class_click(self):
        return {
            GoryouClass.Dark_Divine_Dragon: self.C_DARK_DIVINE_DRAGON,
            GoryouClass.Dark_Hakuzousu: self.C_DARK_HAKUZOUSU,
            GoryouClass.Dark_Black_Panther: self.C_DARK_BLACK_PANTHER,
            GoryouClass.Dark_Peacock: self.C_DARK_PEACOCK
        }

    def choose_class(self) -> bool:
        target_class = self.get_goryou_class(self.gr_class)
        if target_class is None:
            return False

        # 进入御灵战斗界面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_GR_FIGHT_CHECK):
                break

            self.click(self.goryou_class_click[target_class])
        return True

    def choose_level(self):
        if not self.appear(self.I_GR_FIGHT_CHECK):
            raise RequestHumanTakeover("Unrecognized page")

        lv = self.gr_config.level
        lv_match_click = {
            GoryouLevel.one: self.C_LV_1,
            GoryouLevel.two: self.C_LV_2,
            GoryouLevel.three: self.C_LV_3,
        }

        self.class_logger(self.name, f"Assigned level: {lv}")
        self.click(lv_match_click[lv])

    def start_battle(self):
        count_max = self.get_ticket_count()

        for c in range(count_max):
            self.class_logger(
                self.name, f"======== Round {c + 1} Exp Started =========")

            self.wait_and_shot()

            if self.appear(self.I_GR_FIGHT):
                self.click(self.I_GR_FIGHT)
                self.run_battle()

    def get_ticket_count(self):
        image = self.screenshot()
        count = self.O_GR_TICKET_COUNT.digit(image)
        count_max = self.gr_config.count_max
        if count is None:
            raise RequestHumanTakeover("Failed to get ticket number.")

        if count < count_max:
            count_max = count
            logger.warning(
                f"No enough tickets to support max round of battle. Will run battle for [{count}] times.")
        return count_max

    def toggle_realm_team_lock(self, lock: bool = True):
        return self.toggle_team_lock(self.I_GR_TEAM_LOCK, self.I_GR_TEAM_UNLOCK, lock)
