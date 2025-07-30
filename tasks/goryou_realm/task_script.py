import random
from module.base.logger import logger
from tasks.battle.battle import Battle
from tasks.general.page import Page, page_goryou
from tasks.goryou_realm.assets import GoryouRealmAssets as GR
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.control.config.enums import GoryouClass, GoryouLevel

class TaskScript(Battle, GR):
    name = 'Goryou Realm'

    def run(self):
        self.gr_config = self.config.model.goryou_realm.goryou_config
        self.gr_class = self.gr_config.goryou_class
        self.class_match_click = {
            GoryouClass.Dark_Divine_Dragon: self.C_DARK_DIVINE_DRAGON,
            GoryouClass.Dark_Hakuzousu: self.C_DARK_HAKUZOUSU,
            GoryouClass.Dark_Black_Panther: self.C_DARK_BLACK_PANTHER,
            GoryouClass.Dark_Peacock: self.C_DARK_PEACOCK,
        }

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

        # 开始战斗
        self.start_battle()

        self.set_next_run(task='GoryouRealm', finish=True, success=True)
        raise TaskEnd(self.name)

    def choose_random_class(self) -> bool:
        logger.info("Try auto Goryou class")
        classes = list(self.class_match_click.keys())
        random.shuffle(classes)

        # 随机选择一个御灵
        for name in classes:
            self.click(self.class_match_click[name])
            self.wait_and_shot(0.5)
            if self.appear(self.I_GR_FIGHT):
                logger.info("Entered Goryou fight page")
                self.gr_class = name
                return True
        return False

    def choose_class(self) -> bool:
        if self.gr_class is GoryouClass.RANDOM:
            return self.choose_random_class()

        retry = 0
        select_class_failed = False
        while 1:
            if retry > 3:
                logger.error(
                    "Not abled to choose Goryou class. Please check the opening date for selected class.")
                select_class_failed = True
                break

            self.wait_and_shot()
            if self.appear(self.I_GR_FIGHT):
                logger.info("Entered Goryou fight page")
                return True

            if self.appear(self.I_GR_CHECK):
                self.click(self.class_match_click[self.gr_class])
                retry += 1
            else:
                raise RequestHumanTakeover("Unrecognized page")

        if select_class_failed:
            # 尝试随机御灵
            return self.choose_random_class()
        return False

    def choose_level(self):
        if not self.appear(self.I_GR_FIGHT):
            raise RequestHumanTakeover("Unrecognized page")

        lv = self.gr_config.level
        lv_match_click = {
            GoryouLevel.one: self.C_LV_1,
            GoryouLevel.two: self.C_LV_2,
            GoryouLevel.three: self.C_LV_3,
        }

        lv_match_highlight = {
            GoryouLevel.one: self.I_GR_LV_1_HIGHLIGHT,
            GoryouLevel.two: self.I_GR_LV_2_HIGHLIGHT,
            GoryouLevel.three: self.I_GR_LV_3_HIGHLIGHT,
        }

        retry = 0
        while 1:
            self.wait_and_shot()
            if self.appear(lv_match_highlight[lv], 0.95):
                break

            if retry > 3:
                raise RequestHumanTakeover("Failed to choose level")
            self.click(lv_match_click[lv])
            retry += 1

    def start_battle(self):
        count_max = self.get_ticket_count()

        for c in range(count_max):
            logger.info(f"======== Round {c + 1} Exp Started =========")

            ramdon_sleep = random.randint(1, 100) / 100
            self.wait_and_shot(ramdon_sleep)

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
