import time
from tasks.subaccounts.assets import SubaccountsAssets
from tasks.components.page.page import page_main, page_guild
from tasks.components.battle.battle import Battle
from tasks.kekkai.assets import KekkaiAssets as KA

class TaskScript(Battle, KA, SubaccountsAssets):
    def run(self):
        self.goto(page_guild, page_main)
        self.get_guild_money_ep()

        self.goto(page_main, page_guild)

    def get_guild_money_ep(self):
        # 收取每日寮资金和体力
        while 1:
            time.sleep(0.3)
            self.screenshot()
            if not (self.appear(self.I_GUILD_MONEY, 0.96) or self.appear(self.I_GUILD_EP, 0.96)):
                break

            if self.appear(self.I_GUILD_MONEY, 0.96):
                self.click(self.I_GUILD_MONEY)
                if self.wait_until_appear(self.I_GET_GUILD_MONEY, 2):
                    self.click(self.I_GET_GUILD_MONEY)
                    if self.wait_until_appear(self.I_GAIN_REWARD):
                        self.random_click_right()

            if self.appear(self.I_GUILD_EP, 0.96):
                self.click(self.I_GUILD_EP)
                if self.wait_until_appear(self.I_GAIN_REWARD):
                    self.random_click_right()

    def check_kekkai(self):
        # 进入结界
        while 1:
            time.sleep(0.3)
            self.screenshot()
            if self.appear(self.I_GUILD_SKIN_CHANGE):
                break

            if self.appear(self.I_KEKKAI_ENT):
                self.click(self.I_KEKKAI_ENT)

    def get_kekkai_ep(self):
        # 收取体力
        if not self.appear(self.I_EP_BOX):
            return

        while 1:
            time.sleep(0.3)
            self.screenshot()

    def get_kekkai_exp(self):
        # 收取经验
        pass
