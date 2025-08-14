import traceback
from tasks.components.page.assets import PageAssets as PA
from tasks.shikigami_activity.assets import ShikigamiActivityAssets as SA
from tasks.goryou_realm.assets import GoryouRealmAssets as GR

class Page():
    def __init__(self, check_button):
        super().__init__()
        self.check_button = check_button
        self.links = {}
        (filename, line_number, function_name,
         text) = traceback.extract_stack()[-2]
        self.name = text[:text.find('=')].strip()

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def link(self, button, destination):
        self.links[destination] = button


# 主界面 Main
page_main = Page(PA.I_C_MAIN)

# 登录界面
page_login = Page(PA.I_C_LOGIN)
page_login.link(button=PA.C_ENTER_GAME, destination=page_main)

# 召唤界面 Summon
page_summon = Page(PA.I_C_SUMMON)
page_summon.link(button=PA.I_V_SUMMON_TO_MAIN, destination=page_main)
page_main.link(button=PA.I_V_MAIN_TO_SUMMON, destination=page_summon)

# 探索界面 Exploration
page_exp = Page(PA.I_C_EXP)
page_exp.link(button=PA.I_V_EXP_TO_MAIN, destination=page_main)
page_main.link(button=PA.I_V_MAIN_TO_EXP, destination=page_exp)

# 探索章节入口 Exploration Chapter Entrance
page_chapter_entrance = Page(PA.I_C_EXP_MODAL)
page_chapter_entrance.link(
    button=PA.I_V_EXP_MODAL_TO_EXP, destination=page_exp)
page_exp.link(button=PA.I_V_EXP_TO_CH28,
              destination=page_chapter_entrance)

# 结界突破 Realm Raid & Guild Raid
page_realm_raid = Page(PA.I_C_REALM_RAID)
page_realm_raid.link(
    button=PA.I_V_REALM_RAID_TO_EXP, destination=page_exp)
page_exp.link(button=PA.I_V_EXP_TO_REALM_RAID,
              destination=page_realm_raid)

# 商店 Store Street / Market
page_market = Page(PA.I_C_MARKET)
page_market.link(button=PA.I_V_MARKET_TO_MAIN, destination=page_main)

page_store = Page(PA.I_C_GIFT_SHOP)
page_store.link(button=PA.I_V_STORE_TO_MARKET, destination=page_market)
page_main.link(button=PA.I_V_MAIN_TO_STORE, destination=page_store)

# 町中 Town
page_town = Page(PA.I_C_TOWN)
page_town.link(button=PA.I_V_TOWN_TO_MAIN, destination=page_main)
page_main.link(button=PA.I_V_MAIN_TO_TOWN, destination=page_town)

# 町中武馆
page_dojo = Page(PA.I_C_DOJO)
page_dojo.link(button=PA.I_V_DOJO_TO_TOWN, destination=page_town)
page_town.link(button=PA.I_V_TOWN_TO_DOJO, destination=page_dojo)

# 休眠页面 Sleep
page_sleep = Page(PA.I_C_SLEEP)
page_sleep.link(button=PA.I_V_SLEEP_TO_MAIN, destination=page_main)

# 英杰试炼
page_minamoto = Page(PA.I_C_MINAMOTO)
page_minamoto.link(button=PA.I_V_MINAMOTO_TO_EXP, destination=page_exp)
page_exp.link(button=PA.I_V_EXP_TO_MINAMOTO, destination=page_minamoto)

# 式神活动 / 周年庆
page_shikigami = Page(SA.I_SA_CHECK)
page_shikigami.link(button=SA.I_SA_EXIT, destination=page_main)
page_main.link(button=SA.I_SA_ENT, destination=page_shikigami)

# # 阴阳寮
# page_guild = Page(PA.I_C_GUILD)
# page_guild.link(button=PA.I_V_GUILD_TO_MAIN, destination=page_main)
# page_main.link(button=PA.I_V_MAIN_TO_GUILD, destination=page_guild)

# 地域鬼王
page_boss = Page(PA.I_C_BOSS)
page_boss.link(button=PA.I_V_BOSS_TO_EXP, destination=page_exp)
page_exp.link(button=PA.I_V_EXP_TO_BOSS, destination=page_boss)

# 御灵
page_goryou = Page(GR.I_GR_CHECK)
page_goryou.link(button=PA.I_V_GORYOU_TO_EXP, destination=page_exp)
page_exp.link(button=PA.I_V_EXP_TO_GORYOU, destination=page_goryou)

# 契灵之境
page_bonding_fairyland = Page(PA.I_C_FAIRYLAND)
page_bonding_fairyland.link(
    button=PA.I_V_BF_TO_EXP, destination=page_exp)
page_exp.link(button=PA.I_V_EXP_TO_FB,
              destination=page_bonding_fairyland)
