import time
from module.image_processing.rule_image import RuleImage
from tasks.main_page.colla import Colla
from tasks.main_page.task_script import MainPage
from tasks.general.page import page_store, page_main
from module.base.exception import RequestHumanTakeover, TaskEnd
from module.base.logger import logger

class Routine(Colla, MainPage):

    def run_all(self):
        regions = [
            self.I_REGION_YOULONG,
            self.I_REGION_HUAHUO,
            self.I_REGION_SHENZHI,
            self.I_REGION_MAOCHUAN
        ]

        for region in regions:
            self.switch_region(region)
            time.sleep(5)
            self.run_single_account()
            self.switch_account()

            logger.info(f"*** Complete routine for {region.name} ***")

    def run_single_account(self, colla: bool = True):
        self.screenshot()
        if self.appear(self.I_LOGIN_WARNING):
            self.click(self.C_ENTER_GAME)
            time.sleep(5)

        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)
        self.check_shop_pack()
        self.daily_prep()
        if colla:
            self.start_colla()
        self.open_scroll()
        self.get_friends_points()
        self.get_store_gift()
        self.get_huahe()

        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

    def check_shop_pack(self):
        if not self.wait_until_appear(self.I_SHOP_PACK, 1, threshold=0.96):
            return

        while 1:
            self.wait_and_shot()
            if not (self.appear(self.I_SHOP_PACK) or self.appear(self.I_SHOP_PACK_CLOSE)):
                break

            if self.appear(self.I_SHOP_PACK_CLOSE):
                self.click(self.I_SHOP_PACK_CLOSE)
                continue

            if self.appear(self.I_SHOP_PACK):
                self.click(self.I_SHOP_PACK)

    def daily_prep(self):
        while 1:
            self.wait_and_shot()
            if not (self.appear(self.I_MAIL) or
                    self.appear(self.I_GUILD_PACK) or
                    self.appear(self.I_DAILY_BUFF) or
                    self.appear(self.I_DAILY_SIGN)):
                break

            if self.appear(self.I_SIGN, 0.96):
                self.daily_sign()
                continue

            if self.appear(self.I_MAIL, 0.96):
                self.get_mails()
                continue

            if self.appear(self.I_GUILD_PACK, 0.96):
                self.get_guild_pack()
                continue

            if self.appear(self.I_DAILY_BUFF, 0.96):
                self.get_buff_pack()
                continue

        self.get_daily_supply()

    def get_daily_supply(self):
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)
        got_gift = False
        while 1:
            self.wait_and_shot()
            if not (self.appear(self.I_DAILY_EP) or self.appear(self.I_DAILY_JADE)):
                break

            if self.appear(self.I_DAILY_JADE):
                self.click(self.I_DAILY_JADE)
                if self.wait_until_appear(self.I_GAIN_REWARD, 2):
                    got_gift = True
                    self.random_click_right()
                    time.sleep(0.3)
                    self.screenshot()
                    if self.appear(self.I_CLOSE_DAILY_SIGN):
                        self.click(self.I_CLOSE_DAILY_SIGN)
                    continue

            if self.appear(self.I_DAILY_EP):
                self.click(self.I_DAILY_EP)
                if self.wait_until_appear(self.I_GAIN_REWARD, 2):
                    got_gift = True
                    self.random_click_right()

        if got_gift:
            logger.info("==>>> Got all daily gifts")

    def get_buff_pack(self):
        if not self.wait_until_appear(self.I_DAILY_BUFF, 1, threshold=0.96):
            return

        while 1:
            self.wait_and_shot()

            if not (self.appear(self.I_DAILY_BUFF) or self.appear(self.I_GAIN_REWARD)):
                break

            if self.appear(self.I_GAIN_REWARD):
                self.random_click_right()
                break

            if self.appear(self.I_DAILY_BUFF, 0.96):
                self.click(self.I_DAILY_BUFF)

    def toggle_scroll(self, open: bool = True):
        # 打开卷轴
        while open:
            self.wait_and_shot()
            if self.appear(self.I_SCROLL_OPEN):
                return

            if self.appear_then_click(self.I_SCROLL_CLOSE):
                continue

        while not open:
            self.wait_and_shot()
            if self.appear(self.I_SCROLL_CLOSE):
                return

            if self.appear_then_click(self.I_SCROLL_OPEN):
                continue

    def get_huahe(self):
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

            if not (self.appear(self.I_HUAHE_GAIN_REWARD) or self.appear(self.I_GET_ALL_HUAHE, 0.96)):
                break

            if self.appear(self.I_HUAHE_GAIN_REWARD):
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

            if self.appear(self.I_GAIN_REWARD):
                self.random_click_right()
                break

            if self.appear(self.I_GUILD_PACK):
                self.click(self.I_GUILD_PACK)

    def get_store_gift(self):
        self.goto(page_store, page_main)

        # 进入礼包屋
        while 1:
            self.wait_and_shot()

            if self.appear(self.I_STORE_REC, 0.96):
                self.click(self.I_STORE_REC)
                break

            if self.appear(self.I_C_GIFT_SHOP):
                self.click(self.I_C_GIFT_SHOP)

        got_gift = False
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_GAIN_REWARD):
                self.get_reward()
                break

            if self.appear(self.I_STORE_DAILY_REWARD):
                self.click(self.I_STORE_DAILY_REWARD)

        if got_gift:
            logger.info("==>>> Got daily store gift")

        self.goto(page_main, page_store)

    def daily_sign(self):
        if not self.wait_until_appear(self.I_SIGN, 1, threshold=0.96):
            return

        while 1:
            self.wait_and_shot()
            if self.appear(self.I_CLOSE_DAILY_SIGN):
                break

            if self.appear(self.I_REWARD):
                self.random_click_right()
                continue

            if self.appear(self.I_DAILY_SIGN, 0.96):
                self.click(self.I_DAILY_SIGN)
                continue

            if self.appear(self.I_SIGN, 0.96):
                self.click(self.I_SIGN)

        # 退出每日签到
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_SIGN_DOLL):
                break

            if self.appear(self.I_CLOSE_DAILY_SIGN):
                self.click(self.I_CLOSE_DAILY_SIGN)

    def open_scroll(self):
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_SCROLL_OPEN):
                break

            if self.appear_then_click(self.I_SCROLL_CLOSE):
                continue

    def get_mails(self):
        got_mail = False

        if not self.wait_until_appear(self.I_MAIL, 1, threshold=0.96):
            return

        # 进入邮件页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_MAIL_HEADER):
                break

            if self.appear(self.I_MAIL_ENT):
                self.click(self.I_MAIL_ENT)
                continue

        while 1:
            self.wait_and_shot()

            if not self.appear(self.I_MAIL_HEADER):
                break

            if not (self.appear(self.I_GET_ALL_MAIL) or self.appear(self.I_UNREAD_MAIL, 0.98)):
                self.appear_then_click(self.I_MAIL_EXIT)
                continue

            if self.appear(self.I_UNREAD_MAIL, 0.98):
                self.click(self.I_UNREAD_MAIL)
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
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_GET_ALL_FRIEND_POINTS):
                break

            if not self.appear(self.I_FRIEND_POINTS_ENABLE):
                self.click(self.I_FRIEND_POINTS)

                # 跨区好友， 不同区小号专用
                if self.appear(self.I_CROSS_REGION_FRIENDS):
                    self.click(self.I_CROSS_REGION_FRIENDS)

        while 1:
            time.sleep(0.1)
            self.screenshot()
            if self.appear_then_click(self.I_GET_ALL_FRIEND_POINTS):
                if self.wait_until_appear(self.I_GAIN_REWARD, 2):
                    self.random_click_right()
            else:
                break

        self.click(self.I_FRIENDS_EXIT)
        logger.info("==>>> Got all friends points")

    def switch_account(self):
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        # 进入用户界面
        while 1:
            self.click(self.C_AVATAR)

            self.wait_and_shot()
            if self.appear(self.I_USER_CENTER):
                break

        # 返回登录页面
        while 1:
            time.sleep(0.5)
            self.screenshot()
            if self.appear_then_click(self.I_USER_CENTER):
                if self.wait_until_click(self.I_SWITCH_ACCOUNT, 2):
                    continue

            if self.appear_then_click(self.I_LOGIN):
                continue

            if self.appear_then_click(self.I_APPLE_LOGO):
                break

    def switch_region(self, region: RuleImage):
        self.screenshot()
        if not self.appear(self.I_LOGIN_WARNING):
            raise RequestHumanTakeover

        # 进入区域选择页面
        while 1:
            self.wait_and_shot()
            if self.appear(self.I_OWN_CHARACTERS):
                break

            if self.appear(self.I_LOGIN_WARNING) and not self.appear(self.I_PICK_REGION):
                self.click(self.C_REGION)
                continue

            if self.appear(self.I_PICK_REGION):
                if self.wait_until_click(self.I_OPEN_REGIONS, 2, delay=0.5):
                    continue

        # 选区
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_PICK_REGION):
                break

            if self.appear(region, 0.98):
                self.click(region)
                break
            else:
                self.swipe(self.S_REGION_TO_LEFT, duration=500)
                time.sleep(0.5)

        while 1:
            self.wait_and_shot()
            if self.appear(self.I_C_MAIN, 0.95):
                logger.info("==>>> Arrive main page")
                break

            if self.appear(self.I_LOGIN_WARNING):
                self.click(self.C_ENTER_GAME)

    def quest_invite(self):
        # 进入庭院页面
        if not self.check_page_appear(page_main):
            self.goto(page_main)

        # 进去悬赏页面
        while 1:
            self.wait_and_shot()

            if self.appear(self.I_QUEST_HEADER):
                break

            if self.appear(self.I_QUEST):
                self.click(self.I_QUEST)

        # 查看协作任务
        while 1:
            self.wait_and_shot()
            if not self.appear(self.I_QUEST_PLUS_BUTTON):
                break

            if self.appear(self.I_QUEST_PLUS_BUTTON):
                # x, y = self.I_QUEST_PLUS_BUTTON.front_center()
                # self.I_QUEST_JADE.set_area(x, y, 240, 216)
                # if self.appear(self.I_QUEST_JADE):
                self.invite_friend()
                break

    def invite_friend(self):
        while 1:
            self.wait_and_shot()
            if self.appear_then_click(self.I_QUEST_PLUS_BUTTON):
                self.wait_until_click(self.I_CROSS_REGION)
                if self.appear(self.I_CROSS_REGION_ENABLE):
                    time.sleep(1)
                    if self.wait_until_appear(self.I_QUEST_AVATAR, 2, threshold=0.96):
                        x, y = self.I_QUEST_AVATAR.front_center()
                        while 1:
                            time.sleep(0.3)
                            self.screenshot()
                            if self.appear(self.I_QUEST_AVATAR_SELECTED, threshold=0.96):
                                break
                            if self.appear(self.I_QUEST_AVATAR):
                                self.device.click(x + 100, y)
                        self.wait_until_click(self.I_INVITE)
                        break
                    else:
                        self.device.click(1205, 310)
