from pydantic import BaseModel, Field
from module.control.config.enums import *

# 基础设置
class ScriptSetting(BaseModel):
    main_host: str = Field(default="127.0.0.1:16384")
    subhosts: list = Field(default=[
        "16416",
        "16448",
        "16480",
        "16512",
        "16544"
    ])
    accounts: list = Field(default=[
        {
            "account": "abc@abc.com",
            "regions": [
                "1234",
                "456",
                "789"
            ]
        }
    ])

# Daily Routine  每日日常
class DailyRoutine(BaseModel):
    enable: bool = Field(default=False)
    priority: int = Field(default=1, title="优先级")
    enable_jade: bool = Field(default=True)  # 永久勾玉卡
    enable_sign: bool = Field(default=True)  # 签到
    enable_sign_999: bool = Field(default=True)  # 999天的签到福袋
    enable_mail: bool = Field(default=True)  # 邮件
    enable_soul: bool = Field(default=True)  # 御魂加成
    enable_ap: bool = Field(default=True)  # 体力
    one_summon: bool = Field(default=False)  # 每日一抽
    friend_love: bool = Field(default=False)  # 友情点
    store_sign: bool = Field(default=False)  # 商店签到

# 悬赏任务
class WantedQuests(BaseModel):
    accept_type: WantedQuestType = Field(
        default=WantedQuestType.Jade, title="悬赏接受类型")
    invite_friend_name: str = Field(default="", description="邀请指定好友名字")
    invite_type: WantedQuestType = Field(
        default=WantedQuestType.Jade, title="悬赏邀请类型")

# 好友协战（小号用）
class Collaboration(BaseModel):
    enable: bool = Field(default=False)
    priority: int = Field(default=1, title="优先级")
    enable_daily_routine: bool = Field(default=False)

# 个人突破
class RoyalBattle(BaseModel):
    enable: bool = Field(default=False)
    priority: int = Field(default=1, title="优先级")
    grade_threshold: int = Field(title="斗技目标分数", default=2400)

# 绘卷模式
class Exploration(BaseModel):
    enable: bool = Field(default=False)
    priority: int = Field(default=1, title="优先级")
    scroll_mode_enable: bool = Field(default=True)
    scrolls_cd: str = Field(default="0:30:00", title="间隔时间")
    ticket_threshold: int = Field(title="突破票数量", default=25,
                                  description="满足票数后任务自动转去个人突破")
    buff_gold_50: bool = Field(default=False)  # 50%金币加成
    buff_gold_100: bool = Field(default=False)  # 100%金币加成
    buff_exp_50: bool = Field(default=False)  # 50%经验加成
    buff_exp_100: bool = Field(default=False)  # 100%经验加成
    count_max: int = Field(default=7, title="探索次数", description="默认探索7次")
    chapter: Chapters = Field(default=Chapters.CHAPTER_28,
                              title="探索章节", description="探索章节 默认二十八")
    auto_backup: bool = Field(default=False)
    backup_rarity: ChooseRarity = Field(
        title="选择狗粮稀有度", default=ChooseRarity.N, description=ChooseRarity.N)
    lock_team_enable: bool = Field(default=True)  # 锁定队伍


# 式神爬塔活动
class ShikigamiActivity(BaseModel):
    enable: bool = Field(default=False)
    priority: int = Field(default=1, title="优先级")
    enable_ap_mode: bool = Field(default=False)  # 开启体力模式，反之则用活动门票
    auto_switch: bool = Field(default=False)  # 挂完活动门票后自动切换到体力模式
    ticket_max: int = Field(default=50, title="门票爬塔次数",
                            description="默认门票爬塔50次")
    ap_max: int = Field(default=300, title="体力爬塔次数", description="默认体力爬塔300次")
    lock_team_enable: bool = Field(default=True)  # 锁定队伍


# 御灵
class Goryou(BaseModel):
    enable: bool = Field(default=False)
    priority: int = Field(default=1, title="优先级")
    goryou_class: GoryouClass = Field(
        default=GoryouClass.RANDOM, title="御灵")
    count_max: int = Field(default=50, title="御灵次数", description="默认御灵50次")
    level: GoryouLevel = Field(
        default=GoryouLevel.three, title="御灵难度", description="默认御灵难度第三层")
    lock_team_enable: bool = Field(default=True)  # 锁定队伍

class AreaBoss(BaseModel):
    enable: bool = Field(default=False)
    priority: int = Field(default=1, title="优先级")
    boss_number: int = Field(default=3, title="鬼王数量", description="默认3只")

class Summon(BaseModel):
    enable: bool = Field(default=False)
    priority: int = Field(default=1, title="优先级")
    count_max: int = Field(default=300, title="清票数量", description="默认1000张票")
    ticket_threshold: int = Field(
        default=300, title="最少票数", description="默认最少500张票")
