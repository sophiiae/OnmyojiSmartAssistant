from module.image_processing.rule_image import RuleImage
from module.image_processing.rule_ocr import RuleOcr
from module.image_processing.rule_swipe import RuleSwipe
from module.image_processing.rule_click import RuleClick

# This file was automatically generated by ./module/impage_processing/assets_extractor.py.
# Don't modify it manually.
class GeneralAssets: 

	# Image Rule Assets
	# 普通召唤 
	I_REG_SUMMON = RuleImage(
		roi=(448, 605, 42, 58),
		area=(427, 584, 84, 100),
		file="./tasks/general/res/reg_summon.png"
	)
	# 再次召唤 
	I_SUMMON_AGAIN = RuleImage(
		roi=(691, 621, 168, 53),
		area=(665, 595, 220, 105),
		file="./tasks/general/res/summon_again.png"
	)
	# 红色X 
	I_B_RED_X = RuleImage(
		roi=(1184, 112, 46, 46),
		area=(1161, 89, 92, 92),
		file="./tasks/general/res/buttons/b_red_x.png"
	)
	# 蓝色<退出 
	I_B_BLUE_LEFT_ANGLE = RuleImage(
		roi=(24, 36, 53, 44),
		area=(0, 14, 106, 88),
		file="./tasks/general/res/buttons/b_blue_left_angle.png"
	)
	# 黄色<退出 
	I_B_YELLOW_LEFT_ANGLE = RuleImage(
		roi=(34, 9, 42, 41),
		area=(10, 0, 86, 81),
		file="./tasks/general/res/buttons/b_yellow_left_angle.png"
	)
	# 获得奖励栏标 
	I_GAIN_REWARD = RuleImage(
		roi=(476, 233, 329, 42),
		area=(312, 212, 658, 84),
		file="./tasks/general/res/gain_reward.png"
	)
	# 战斗/突破/宝箱奖励领取图标 
	I_REWARD = RuleImage(
		roi=(565, 444, 137, 165),
		area=(497, 376, 273, 301),
		file="./tasks/general/res/reward.png"
	)

	# Ocr Rule Assets
	# 普通召唤票数量 
	O_REG_SUMMON_TICKET = RuleOcr(
		roi=(565, 15, 80, 29),
		area=(565, 15, 80, 29),
		keyword="",
		name="reg_summon_ticket"
	)

	# Image Rule Assets
	# 主界面 
	I_C_MAIN = RuleImage(
		roi=(905, 134, 48, 48),
		area=(600, 110, 500, 96),
		file="./tasks/general/res/check/c_main.png"
	)
	# 探索界面妖标志 
	I_C_EXP = RuleImage(
		roi=(62, 642, 49, 41),
		area=(42, 622, 89, 81),
		file="./tasks/general/res/check/c_exp.png"
	)
	# 章节入口探索标志 
	I_C_EXP_MODAL = RuleImage(
		roi=(1064, 233, 62, 108),
		area=(1033, 202, 124, 170),
		file="./tasks/general/res/check/c_exp_modal.png"
	)
	# 商店街建筑 
	I_C_MARKET = RuleImage(
		roi=(258, 470, 58, 44),
		area=(229, 448, 116, 88),
		file="./tasks/general/res/check/c_market.png"
	)
	# 礼包屋标志 
	I_C_GIFT_SHOP = RuleImage(
		roi=(1141, 646, 61, 38),
		area=(1122, 627, 99, 76),
		file="./tasks/general/res/check/c_gift_shop.png"
	)
	# 召唤界面蓝票 
	I_C_SUMMON = RuleImage(
		roi=(597, 606, 64, 59),
		area=(567, 576, 124, 119),
		file="./tasks/general/res/check/c_summon.png"
	)
	# 个人突破结界突破点亮标志 
	I_C_REALM_RAID = RuleImage(
		roi=(1196, 231, 69, 112),
		area=(1162, 197, 137, 180),
		file="./tasks/general/res/check/c_realm_raid.png"
	)
	# 阴阳寮寮信息图标 
	I_C_GUILD = RuleImage(
		roi=(1167, 617, 77, 58),
		area=(1138, 588, 135, 116),
		file="./tasks/general/res/check/c_guild.png"
	)
	# 阴阳寮突破突破点亮标志 
	I_C_GUILD_RAID = RuleImage(
		roi=(1196, 355, 69, 111),
		area=(1162, 321, 137, 179),
		file="./tasks/general/res/check/c_guild_raid.png"
	)
	# 休眠模式音乐按钮 
	I_C_SLEEP = RuleImage(
		roi=(1182, 637, 57, 45),
		area=(1154, 614, 114, 90),
		file="./tasks/general/res/check/c_sleep.png"
	)
	# 英杰试炼源氏补给图标 
	I_C_MINAMOTO = RuleImage(
		roi=(60, 615, 46, 50),
		area=(37, 592, 92, 96),
		file="./tasks/general/res/check/c_minamoto.png"
	)
	# 地域鬼王集结图标 
	I_C_BOSS = RuleImage(
		roi=(35, 628, 86, 50),
		area=(10, 603, 136, 100),
		file="./tasks/general/res/check/c_boss.png"
	)
	# 召唤页面退出 
	I_V_SUMMON_TO_MAIN = RuleImage(
		roi=(34, 9, 42, 41),
		area=(14, 0, 82, 81),
		file="./tasks/general/res/buttons/b_yellow_left_angle.png"
	)
	# 探索章节入口退出 
	I_V_EXP_MODAL_TO_EXP = RuleImage(
		roi=(1025, 129, 46, 46),
		area=(1002, 106, 92, 92),
		file="./tasks/general/res/buttons/b_red_x.png"
	)
	# 探索界面返回主界面 
	I_V_EXP_TO_MAIN = RuleImage(
		roi=(30, 36, 53, 44),
		area=(4, 14, 106, 88),
		file="./tasks/general/res/buttons/b_blue_left_angle.png"
	)
	# 商店街退出 
	I_V_MARKET_TO_MAIN = RuleImage(
		roi=(24, 36, 53, 44),
		area=(2, 14, 97, 88),
		file="./tasks/general/res/buttons/b_blue_left_angle.png"
	)
	# 商店退出到商店街 
	I_V_STORE_TO_MARKET = RuleImage(
		roi=(30, 16, 42, 41),
		area=(10, 0, 82, 81),
		file="./tasks/general/res/buttons/b_yellow_left_angle.png"
	)
	# 英杰试炼退出 
	I_V_MINAMOTO_TO_EXP = RuleImage(
		roi=(20, 16, 42, 41),
		area=(0, 0, 82, 81),
		file="./tasks/general/res/buttons/b_yellow_left_angle.png"
	)
	# 阴阳寮退出 
	I_V_GUILD_TO_MAIN = RuleImage(
		roi=(30, 18, 42, 41),
		area=(10, 0, 82, 81),
		file="./tasks/general/res/buttons/b_yellow_left_angle.png"
	)
	# 结界突破退出 
	I_V_REALM_RAID_TO_EXP = RuleImage(
		roi=(1184, 112, 46, 46),
		area=(1161, 89, 92, 92),
		file="./tasks/general/res/buttons/b_red_x.png"
	)
	#  
	I_V_BOSS_TO_EXP = RuleImage(
		roi=(45, 35, 53, 44),
		area=(23, 13, 97, 88),
		file="./tasks/general/res/buttons/b_blue_left_angle.png"
	)
	# 主界面探索灯笼 
	I_V_MAIN_TO_EXP = RuleImage(
		roi=(655, 102, 55, 87),
		area=(490, 58, 600, 174),
		file="./tasks/general/res/goto/v_main_to_exp.png"
	)
	# 第二十八章位置（在最底下的时候） 
	I_V_EXP_TO_CH28 = RuleImage(
		roi=(1058, 493, 189, 94),
		area=(1011, 446, 268, 188),
		file="./tasks/general/res/goto/v_exp_to_ch28.png"
	)
	# 主界面阴阳寮入口 
	I_V_MAIN_TO_GUILD = RuleImage(
		roi=(542, 602, 47, 53),
		area=(518, 576, 94, 106),
		file="./tasks/general/res/goto/v_main_to_guild.png"
	)
	# 主界面召唤灯笼 
	I_V_MAIN_TO_SUMMON = RuleImage(
		roi=(1081, 170, 35, 76),
		area=(1064, 132, 70, 152),
		file="./tasks/general/res/goto/v_main_to_summon.png"
	)
	# 主界面町中入口 
	I_V_MAIN_TO_TOWN = RuleImage(
		roi=(713, 250, 52, 40),
		area=(687, 230, 104, 80),
		file="./tasks/general/res/goto/v_main_to_town.png"
	)
	# 探索界面寮突破入口 
	I_V_EXP_TO_REALM_RAID = RuleImage(
		roi=(251, 635, 58, 52),
		area=(222, 609, 116, 104),
		file="./tasks/general/res/goto/v_exp_to_realm_raid.png"
	)
	# 寮突破按钮 
	I_V_REALM_RAID_TO_GUILD_RAID = RuleImage(
		roi=(1203, 359, 54, 102),
		area=(1176, 308, 108, 204),
		file="./tasks/general/res/goto/v_realm_raid_to_guild_raid.png"
	)
	# 个人突破按钮 
	I_V_GUILD_RAID_TO_REALM_RAID = RuleImage(
		roi=(1203, 236, 54, 101),
		area=(1176, 186, 108, 202),
		file="./tasks/general/res/goto/v_guild_raid_to_realm_raid.png"
	)
	# 休眠模式退出 
	I_V_SLEEP_TO_MAIN = RuleImage(
		roi=(27, 28, 38, 36),
		area=(8, 10, 76, 72),
		file="./tasks/general/res/goto/v_sleep_to_main.png"
	)
	# 商店入口 
	I_V_MAIN_TO_STORE = RuleImage(
		roi=(643, 616, 68, 56),
		area=(609, 588, 136, 112),
		file="./tasks/general/res/goto/v_main_to_store.png"
	)
	# 英杰试炼入口 
	I_V_EXP_TO_MINAMOTO = RuleImage(
		roi=(837, 639, 60, 46),
		area=(814, 616, 106, 92),
		file="./tasks/general/res/goto/v_exp_to_minamoto.png"
	)
	# 地域鬼王入口 
	I_V_EXP_TO_BOSS = RuleImage(
		roi=(641, 638, 60, 47),
		area=(617, 614, 108, 95),
		file="./tasks/general/res/goto/v_exp_to_boss.png"
	)


