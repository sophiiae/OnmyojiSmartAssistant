"""
Configuration base models for Onmyoji automation system.

This module defines the base configuration classes using Pydantic models
for type validation and serialization. It provides structured configuration
for various game automation tasks.
"""

from pydantic import BaseModel, Field
from module.config.enums import *

class DeviceSetting(BaseModel):
    """
    Device connection and control settings.

    Attributes:
        serial (str): Device serial in format "host:port" (e.g., "127.0.0.1:16416")
        screenshot_method (ScreenshotMethod): Method to capture screenshots
        control_method (ControlMethod): Method to control device input
    """

    serial: str = Field(
        default="127.0.0.1:16416",
        description="Device serial in format 'host:port' for ADB connection"
    )

class Optimization(BaseModel):
    """
    Performance optimization settings.

    These settings control timing and performance aspects of the automation
    to balance between speed and resource usage.
    """

    # Screenshot interval settings
    screenshot_interval: float = Field(
        default=0.3,
        ge=0.1,
        le=0.3,
        description="Minimum interval between screenshots (seconds). "
        "Lower values increase CPU usage but improve responsiveness."
    )

    combat_screenshot_interval: float = Field(
        default=1.0,
        ge=0.1,
        le=1.0,
        description="Minimum interval between screenshots during combat (seconds). "
        "Longer intervals reduce CPU usage during battles."
    )

    # Task scheduling settings
    schedule_rule: ScheduleRule = Field(
        default=ScheduleRule.FIFO,
        description="Rule for scheduling multiple pending tasks"
    )

class ErrorHandler(BaseModel):
    """
    Error handling configuration.

    Defines how the system should respond to various error conditions
    during automation execution.
    """

    when_network_abnormal: ErrorHandleMethod = Field(
        default=ErrorHandleMethod.wait_10s,
        title="Network Abnormal Response",
        description="Action to take when network appears unstable but functional"
    )

    when_network_error: ErrorHandleMethod = Field(
        default=ErrorHandleMethod.restart,
        title="Network Error Response",
        description="Action to take when network connection fails completely"
    )

    cache_clear_request: bool = Field(
        default=True,
        description="Whether to automatically clear cache when errors occur"
    )

# 基础设置
class ScriptSetting(BaseModel):
    """
    Core script configuration containing device, optimization, and error handling settings.

    This is the main configuration container for system-level settings.
    """

    device: DeviceSetting = Field(
        default_factory=DeviceSetting,
        description="Device connection and control settings"
    )

    regions: list[str] = Field(
        default=[],
        description="Regions to run the script in"
    )

class Scheduler(BaseModel):
    """
    Task scheduling configuration.

    Controls when and how frequently tasks should be executed.
    """

    enable: bool = Field(
        default=False,
        description="Whether this task is enabled for execution"
    )

    next_run: str = Field(
        default="2024-08-16 21:13:17",
        description="Next scheduled execution time in format 'YYYY-MM-DD HH:MM:SS'"
    )

    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Task priority (1=highest, 10=lowest)"
    )

    success_interval: str = Field(
        default="00 00:10:00",
        description="Interval before next run after successful completion (DD HH:MM:SS)"
    )

    failure_interval: str = Field(
        default="00 00:10:00",
        description="Interval before retry after failure (DD HH:MM:SS)"
    )

class SwitchSoulConfig(BaseModel):
    enable: bool = Field(default=False)
    switch_group_team: str = Field(
        default='-1,-1', description='switch_group_team_help')

class HarvestConfig(BaseModel):
    """
    Daily harvest/collection task configuration.

    Controls which daily collection activities should be automated.
    """

    enable_jade: bool = Field(
        default=True,
        description="永久勾玉卡"
    )

    enable_sign: bool = Field(
        default=True,
        description="签到"
    )

    enable_sign_999: bool = Field(
        default=True,
        description="999天的签到福袋"
    )

    enable_mail: bool = Field(
        default=True,
        description="邮件"
    )

    enable_soul: bool = Field(
        default=True,
        description="御魂加成"
    )

    enable_ap: bool = Field(
        default=True,
        description="体力"
    )

class TriflesConfig(BaseModel):
    """
    每日设置（包含签到、体力、御魂加成、邮件、永久勾玉卡、999天的签到福袋）
    """

    one_summon: bool = Field(
        default=False,
        description="每日一抽"
    )

    guild_wish: bool = Field(
        default=False,
        description="寮祈愿"
    )

    friend_love: bool = Field(
        default=False,
        description="友情点"
    )

    store_sign: bool = Field(
        default=False,
        description="商店签到"
    )

# Daily Routine  每日日常
class DailyRoutine(BaseModel):
    """
    每日日常设置
    """

    scheduler: Scheduler = Field(
        default_factory=Scheduler,
        description="Scheduling configuration for daily routine"
    )

    harvest_config: HarvestConfig = Field(
        default_factory=HarvestConfig,
        description="Configuration for main daily collection tasks"
    )

    trifles_config: TriflesConfig = Field(
        default_factory=TriflesConfig,
        description="Configuration for optional daily tasks"
    )

class QuestInviteConfig(BaseModel):
    """
    悬赏封印邀请配置
    """
    invite_friend_name: str = Field(
        default="无",
        description="邀请指定好友名字"
    )

    invite_jade: bool = Field(
        default=False,
        description="接受勾玉悬赏"
    )

    invite_ap: bool = Field(
        default=False,
        description="接受体力悬赏"
    )

    invite_virtual: bool = Field(
        default=False,
        description="接受虚拟悬赏"
    )

    invite_pet_food: bool = Field(
        default=False,
        description="接受宠物粮悬赏"
    )

class AcceptQuestConfig(BaseModel):
    """
    悬赏封印接受配置
    """
    accept_jade: bool = Field(
        default=False,
        description="接受勾玉悬赏"
    )

    accept_ap: bool = Field(
        default=False,
        description="接受体力悬赏"
    )

    accept_virtual: bool = Field(
        default=False,
        description="接受虚拟悬赏"
    )

    accept_pet_food: bool = Field(
        default=False,
        description="接受宠物粮悬赏"
    )

# 协作任务
class WantedQuests(BaseModel):
    """
    协作任务接受配置
    """

    accept_quest_config: AcceptQuestConfig = Field(
        default_factory=AcceptQuestConfig,
        description="协作任务接受配置"
    )

    invite_quest_config: QuestInviteConfig = Field(
        default_factory=QuestInviteConfig,
        description="协作任务邀请配置"
    )

class RaidConfig(BaseModel):
    """
    个人突破设置
    """
    enable_guild_realm_raid: bool = Field(
        default=False,
        description="寮突破模式"
    )

    tickets_required: int = Field(
        default=20,
        ge=1,
        description="突破所需门票数量"
    )

    when_attack_fail: str = Field(
        default="Continue",
        description="战斗失败设置"
    )

# 个人突破
class RealmRaid(BaseModel):
    """
    个人突破配置
    """

    scheduler: Scheduler = Field(
        default_factory=Scheduler,
        description="Scheduling configuration for realm raid"
    )

    raid_config: RaidConfig = Field(
        default_factory=RaidConfig,
        description="Raid-specific configuration settings"
    )

    switch_soul_config: SwitchSoulConfig = Field(
        default_factory=SwitchSoulConfig,
        description="御魂切换配置"
    )

class ExplorationConfig(BaseModel):
    """
    Exploration task configuration.

    Settings for chapter exploration and experience/gold farming.
    """
    # Buff settings
    buff_gold_50: bool = Field(
        default=False,
        description="50%金币加成"
    )

    buff_gold_100: bool = Field(
        default=False,
        description="100%金币加成"
    )

    buff_exp_50: bool = Field(
        default=False,
        description="50%经验加成"
    )

    buff_exp_100: bool = Field(
        default=False,
        description="100%经验加成"
    )

    # Exploration settings
    count_max: int = Field(
        default=7,
        ge=1,
        title="探索次数",
        description="探索最大次数，默认探索7次"
    )

    chapter: Chapters = Field(
        default=Chapters.CHAPTER_28,
        title="探索章节",
        description="探索章节 默认二十八"
    )

    chapter_hardness: ChapterHardness = Field(
        default=ChapterHardness.HARD,
        title="探索难度",
        description="探索难度 默认困难"
    )

    # Backup/fodder settings
    auto_backup: bool = Field(
        default=False,
        description="狗粮没了之后自动补全"
    )

    auto_soul_clear: bool = Field(
        default=False,
        description="自动清废御魂"
    )

    backup_rarity: ChooseRarity = Field(
        title="Backup Rarity Selection",
        default=ChooseRarity.N,
        description="选择狗粮稀有度"
    )

    # Team settings
    lock_team_enable: bool = Field(
        default=True,
        description="锁定阵容"
    )


class ScrollMode(BaseModel):
    """
    绘卷模式配置
    """

    scroll_mode_enable: bool = Field(
        default=True,
        description="绘卷模式"
    )

    scrolls_cd: str = Field(
        default="0:30:00",
        description="绘卷冷却时间"
    )

    ticket_threshold: int = Field(
        default=23,
        ge=1,
        description="绘卷门票阈值"
    )

# 探索
class Exploration(BaseModel):
    """
    探索配置
    """

    scheduler: Scheduler = Field(
        default_factory=Scheduler,
        description="探索任务调度"
    )

    exploration_config: ExplorationConfig = Field(
        default_factory=ExplorationConfig,
        title="探索设置",
        description="探索设置"
    )

    scroll_mode: ScrollMode = Field(
        default_factory=ScrollMode,
        description="绘卷模式配置"
    )

    switch_soul_config: SwitchSoulConfig = Field(
        default_factory=SwitchSoulConfig,
        description="御魂切换配置"
    )

class ClimbConfig(BaseModel):
    """
    Climbing tower configuration for events.

    Settings for automated tower climbing during events.
    """

    enable_ap_mode: bool = Field(
        default=False,
        description="开启体力模式，反之则用活动门票"
    )

    auto_switch: bool = Field(
        default=False,
        description="门票耗尽后自动切换到体力模式"
    )

    anniversary_mode: bool = Field(
        default=False,
        description="周年庆模式"
    )

    demon_king_mode: bool = Field(
        default=False,
        description="超鬼王模式"
    )

    ticket_max: int = Field(
        default=50,
        ge=1,
        le=999,
        title="门票爬塔次数",
        description="门票爬塔次数， 默认门票爬塔50次"
    )

    ap_max: int = Field(
        default=300,
        ge=1,
        title="体力爬塔次数",
        description="体力爬塔次数， 默认体力爬塔300次"
    )

    lock_team_enable: bool = Field(
        default=True,
        description="锁定阵容"
    )

# 式神爬塔活动
class ShikigamiActivity(BaseModel):
    """
    式神爬塔活动配置
    """

    scheduler: Scheduler = Field(
        default_factory=Scheduler,
        description="式神爬塔活动调度"
    )

    climb_config: ClimbConfig = Field(
        default_factory=ClimbConfig,
        description="式神爬塔活动配置"
    )

    switch_soul_config: SwitchSoulConfig = Field(
        default_factory=SwitchSoulConfig,
        description="御魂切换配置"
    )

# 御灵
class GoryouConfig(BaseModel):
    """
    御灵配置
    """

    goryou_class: GoryouClass = Field(
        default=GoryouClass.RANDOM,
        title="御灵类型",
        description="御灵类型， 默认随机"
    )

    count_max: int = Field(
        default=50,
        ge=1,
        title="御灵次数",
        description="御灵次数， 默认御灵50次"
    )

    level: GoryouLevel = Field(
        default=GoryouLevel.three,
        title="御灵难度",
        description="御灵难度，默认御灵难度第三层"
    )

    lock_team_enable: bool = Field(
        default=True,
        description="锁定阵容"
    )

class GoryouRealm(BaseModel):
    """
    御灵配置
    """

    scheduler: Scheduler = Field(
        default_factory=Scheduler,
        description="御灵任务调度"
    )

    goryou_config: GoryouConfig = Field(
        default_factory=GoryouConfig,
        description="御灵配置"
    )

    switch_soul_config: SwitchSoulConfig = Field(
        default_factory=SwitchSoulConfig,
        description="御魂切换配置"
    )

class AreaBossConfig(BaseModel):
    """
    鬼王设置
    """
    boss_number: int = Field(
        default=3,
        title="地域鬼王数量",
        description="默认3只，只打前3只鬼王"
    )

    boss_reward: bool = Field(
        default=False,
        description="是否打当日的悬赏鬼王"
    )

class AreaBoss(BaseModel):
    """
    地域鬼王
    """
    scheduler: Scheduler = Field(
        default_factory=Scheduler,
        description="御灵任务调度"
    )

    boss_config: AreaBossConfig = Field(
        default_factory=AreaBossConfig,
        description="地域鬼王设置"
    )

    switch_soul_config: SwitchSoulConfig = Field(
        default_factory=SwitchSoulConfig,
        description="御魂切换配置"
    )


class DuelConfig(BaseModel):
    """
    斗技段位
    """
    elite: bool = Field(
        default=False,
        description="是否上名士"
    )

    tier: DuelTier = Field(
        default=DuelTier.tier_1,
        description="斗技段位"
    )

    full_honor_points: bool = Field(
        default=False,
        description="是否打满荣誉积分"
    )

    onmyoji: OnmyojiClass = Field(
        default=OnmyojiClass.AUTO,
        description="斗技阴阳师"
    )

class Duel(BaseModel):
    """
    斗技
    """
    scheduler: Scheduler = Field(
        default_factory=Scheduler,
        description="斗技任务调度"
    )

    duel_config: DuelConfig = Field(
        default_factory=DuelConfig,
        description="斗技配置"
    )

    switch_soul_config: SwitchSoulConfig = Field(
        default_factory=SwitchSoulConfig,
        description="御魂切换配置"
    )

class BondingConfig(BaseModel):
    explore_count: int = Field(
        default=30,
        title="探查次数",
        description="探查最大次数"
    )

    lock_team_enable: bool = Field(
        default=True,
        description="锁定阵容"
    )

class BondingFairyland(BaseModel):
    """
    契灵之境
    """
    scheduler: Scheduler = Field(
        default_factory=Scheduler,
        description="斗技任务调度"
    )

    bonding_config: BondingConfig = Field(
        default_factory=BondingConfig,
        description="契灵探查配置"
    )

    switch_soul_config: SwitchSoulConfig = Field(
        default_factory=SwitchSoulConfig,
        description="御魂切换配置"
    )
