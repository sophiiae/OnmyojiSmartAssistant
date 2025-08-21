import time
from tasks.components.battle.battle import Battle
from tasks.components.page.page import page_store, page_main
from tasks.daily_routine.assets import DailyRoutineAssets
from module.base.exception import TaskEnd
from module.base.logger import logger

class TaskScript(Battle, DailyRoutineAssets):
    name = "DailyRoutine"

    @property
    def harvest_config(self):
        havest_config = self.config.model.daily_routine.harvest_config
        return havest_config.model_dump()

    def run(self):
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        self.check_shop_pack()
        self.check_harvest()
        # self.get_talisman_pass_reward()

        self.set_next_run(self.name, success=True, finish=True)
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        raise TaskEnd(self.name)

    def check_shop_pack(self):
        if not self.wait_until_appear(self.I_SHOP_PACK, 1, threshold=0.96):
            return

        # 商店礼包推荐
        while 1:
            self.wait_and_shot()
            if not (self.appear(self.I_SHOP_PACK) or self.appear(self.I_SHOP_PACK_CLOSE)):
                break

            if self.appear_then_click(self.I_SHOP_PACK_CLOSE):
                continue

            self.appear_then_click(self.I_SHOP_PACK)

    def check_harvest(self):
        sign = self.harvest_config["enable_sign"]
        get_mail = self.harvest_config["enable_mail"]

        while 1:
            self.wait_and_shot()
            if not (self.appear(self.I_MAIL) or
                    self.appear(self.I_GUILD_PACK) or
                    self.appear(self.I_DAILY_BUFF) or
                    self.appear(self.I_DAILY_SIGN)):
                break

            if sign and self.appear(self.I_SIGN, 0.96):
                self.daily_lot()
                continue

            if get_mail and self.appear(self.I_MAIL, 0.96):
                self.get_mails()
                continue

            if get_mail and self.appear(self.I_GUILD_PACK, 0.96):
                self.get_guild_pack()
                continue

            if self.appear(self.I_DAILY_BUFF, 0.96):
                self.get_buff_pack()
                continue

        get_jade = self.harvest_config["enable_jade"]
        get_ap = self.harvest_config["enable_ap"]
        if not (get_jade or get_ap):
            return

        self.class_logger(self.name, "Getting jade / ap. ")
        # 拿勾玉和体力
        while 1:
            self.wait_and_shot()
            if not (self.appear(self.I_DAILY_AP) or self.appear(self.I_DAILY_JADE)):
                break

            if get_jade and self.appear(self.I_DAILY_JADE):
                self.click(self.I_DAILY_JADE)
                if self.gain_reward():
                    self.appear_then_click(self.I_CLOSE_DAILY_SIGN)
                    continue

            if get_ap and self.appear(self.I_DAILY_AP):
                self.click(self.I_DAILY_AP)
                self.gain_reward()

                self.toggle_scroll(True)

        if self.harvest_config["friend_love"]:
            self.get_friends_points()

        if self.harvest_config["store_sign"]:
            self.get_store_gift()

        # TODO: one_summon

    def get_buff_pack(self):
        if not self.wait_until_appear(self.I_DAILY_BUFF, 1, threshold=0.96):
            return

        while 1:
            self.wait_and_shot()

            if not (self.appear(self.I_DAILY_BUFF) or self.appear(self.I_GAIN_REWARD)):
                break

            if self.gain_reward():
                break

            self.appear_then_click(self.I_DAILY_BUFF, 0.96)

    def get_talisman_pass_reward(self):
        self.toggle_scroll()
        # 进入花合战
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_GET_ALL_HUAHE):
                break

            if self.appear_then_click(self.I_HUAHE):
                continue

        # 领取奖励
        while 1:
            self.wait_and_shot()

            if not (self.appear(self.I_GAIN_REWARD) or self.appear(self.I_GET_ALL_HUAHE, 0.96)):
                break

            if self.appear(self.I_GAIN_REWARD):
                self.random_click_right()
                continue

            if self.appear(self.I_GET_ALL_HUAHE, 0.96):
                self.click(self.I_GET_ALL_HUAHE)

        # 退出花合战
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_MAIN, 0.96):
                break

            self.click(self.C_EXIT_HUAHE)

    def get_guild_pack(self):
        if not self.wait_until_appear(self.I_GUILD_PACK, 1, threshold=0.96):
            return

        while 1:
            self.wait_and_shot()
            if self.gain_reward():
                break
            self.appear_then_click(self.I_GUILD_PACK)
            time.sleep(0.5)

    def get_store_gift(self):
        self.goto(page_store, page_main)

        # 进入礼包屋
        while 1:
            self.wait_and_shot()
            if self.appear_then_click(self.I_DAILY_LANTERN, 0.96):
                break

            self.appear_then_click(self.I_C_GIFT_SHOP)

        retry = 0
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_GAIN_REWARD):
                self.get_reward()
                break

            if retry > 3:
                break

            self.appear_then_click(self.I_DAILY_REWARD)
            retry += 1

        self.goto(page_main, page_store)

    def daily_lot(self):
        self.class_logger(self.name, "Daily lot")
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_CLOSE_DAILY_SIGN, 0.95):
                break

            if self.appear(self.I_REWARD):
                self.random_click_right()
                continue

            if self.appear_then_click(self.I_DAILY_SIGN, 0.96):
                continue

            self.appear_then_click(self.I_SIGN, 0.96)

        # 退出每日签到
        self.click_static_target(self.I_CLOSE_DAILY_SIGN)

    def get_mails(self):
        got_mail = False

        if not self.wait_until_appear(self.I_MAIL, 1, threshold=0.96):
            return

        # 进入邮件页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_MAIL_HEADER):
                break

            self.appear_then_click(self.I_MAIL_ENT)

        while 1:
            self.wait_and_shot()

            if not self.appear(self.I_MAIL_HEADER):
                break

            if not (self.appear(self.I_GET_ALL_MAIL) or self.appear(self.I_UNREAD_MAIL, 0.98)):
                self.appear_then_click(self.I_MAIL_EXIT)
                continue

            if self.appear_then_click(self.I_UNREAD_MAIL, 0.98):
                continue

            if self.appear_then_click(self.I_GET_ALL_MAIL):
                if self.wait_until_click(self.I_MAIL_CONFIRM, 2):
                    if self.wait_until_appear(self.I_GAIN_REWARD, 2):
                        got_mail = True
                        self.random_click_right()
                        continue

        if got_mail:
            logger.info("==>>> Got all mails")

    def get_friends_points(self):
        """收取友情点
        """
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        # 打开卷轴
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_SCROLL_OPEN):
                break

            if self.appear_then_click(self.I_SCROLL_CLOSE):
                continue

        # 进入好友页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_FRIEND_HEADER):
                break

            if self.appear_then_click(self.I_FRIENDS):
                continue

        # 收取友情点
        retry = 0
        find_points = True
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_GET_ALL_FRIEND_POINTS):
                break

            if retry > 3:
                find_points = False
                break

            if not self.appear(self.I_FRIEND_POINTS_ENABLE):
                self.click(self.I_FRIEND_POINTS)

                # 跨区好友， 不同区小号专用
                self.appear_then_click(self.I_CROSS_REGION_FRIENDS)
            retry += 1

        while find_points:
            self.wait_and_shot()
            if self.appear_then_click(self.I_GET_ALL_FRIEND_POINTS):
                if self.wait_until_appear(self.I_GAIN_REWARD, 2):
                    self.random_click_right()
            else:
                break

        self.click(self.I_FRIENDS_EXIT)
        logger.info("==>>> Got all friends points")
