import os
import subprocess
import time
import pyautogui

from single_start import check_mumu_process, connect_adb
from close_all import kill_mumu_process

def get_image_path(file_name: str) -> str:
    """获取图片文件的绝对路径"""
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, '../res/', file_name)


# ===== 配置区域（根据你的环境修改）=====
CONFIG = {
    # MuMu多开器路径（默认MuMu12）
    "mumu_multi_player_path": r"C:\Program Files\Netease\MuMu Player 12\shell\MuMuMultiPlayer.exe",

    # 要启动的实例配置（名称 + ADB端口）
    "instances": [
        {"name": "浅", "adb_port": 16384},
        {"name": "念", "adb_port": 16416},
        {"name": "小", "adb_port": 16448},
        {"name": "3", "adb_port": 16480},
        {"name": "4", "adb_port": 16512},
        {"name": "5", "adb_port": 16544},
    ],

    # 游戏配置
    "game": {
        "package": "com.netease.onmyoji",  # 官服包名
        "main_activity": "com.netease.onmyoji.MainActivity",  # 主Activity
        "launch_method": "input_tap",  # 可选 "am_start" 或 "input_tap"
        "tap_coordinates": {"x": 955, "y": 333}  # 点击坐标（input_tap时生效）
    },

    # 高级设置
    "delay_between_instances": 15,  # 实例启动间隔（秒）
    "max_retries": 2               # 失败重试次数
}

def start_mumu_multi():
    # 检查MuMu12是否已经运行
    try:
        # 使用tasklist命令检查MuMu12进程
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq MuMuPlayer.exe'],
                                capture_output=True, text=True)
        if 'MuMuPlayer.exe' in result.stdout:
            print("MuMu12模拟器已经在运行中。")
            return True
    except Exception as e:
        print(f"检查MuMu12进程时出错: {e}")
        return False

    if not os.path.exists(CONFIG["mumu_multi_player_path"]):
        print(f"未找到MuMu12多开器，请确认安装路径是否正确: {CONFIG["mumu_multi_player_path"]}")
        return False

    # 启动MuMu12多开器
    try:
        print("正在启动MuMu12多开器...")
        subprocess.Popen([CONFIG["mumu_multi_player_path"]])
        while 1:
            time.sleep(2)  # 等待多开器启动
            # 检查MuMu12多开器是否启动成功
            if check_mumu_process():
                print("MuMu12多开器已启动成功！")
                break
            else:
                print("等待MuMu12多开器启动...")
        return True
    except Exception as e:
        print(f"启动MuMu12多开器时出错: {e}")
        return False

def activate_all_mumu() -> bool:
    if not start_mumu_multi():  # 启动MuMu多开器
        return False

    print("正在激活所有MuMu模拟器...")
    while 1:
        time.sleep(2)  # 等待多开器启动
        # 检查MuMu12多开器是否启动成功
        if check_mumu_process():
            print("MuMu12多开器已启动成功！")
            break
        else:
            print("等待MuMu12多开器启动...")

    try:
        select_all = pyautogui.locateOnScreen(
            get_image_path('select_all.png'), confidence=0.9, region=(1350, 750, 200, 70))
        if select_all is not None:
            print("✅ 找到MuMu12多开器的全选栏，正在激活...")
            pyautogui.click(1395, 785)  # 点击全选栏位置
            time.sleep(1)
    except pyautogui.ImageNotFoundException:
        print("❌ 未找到MuMu12多开器的全选栏，请检查图片路径和截图质量！")
        return False

    try:
        start_all = pyautogui.locateOnScreen(
            get_image_path('start_all.png'), confidence=0.9, region=(1350, 1450, 100, 100))
        if start_all is not None:
            print("✅ 找到MuMu12多开器的全部开始按钮，正在点击...")
            pyautogui.click(start_all)
    except pyautogui.ImageNotFoundException:
        print("❌ 未找到MuMu12多开器的开始按钮，请检查图片路径和截图质量！")
        return False

    time.sleep(20)  # 等待模拟器启动完成
    print("✅ 所有MuMu模拟器已激活！")
    if not connect_all_adb():  # 连接所有MuMu实例的ADB
        return False

    print("正在关闭MuMu多开器...")
    kill_mumu_process(multi_only=True)  # 关闭多开器进程
    print("✅ MuMu多开器已关闭。")
    return True

def connect_all_adb() -> bool:
    """连接所有MuMu实例的ADB"""
    for instance in CONFIG["instances"]:
        print(f"\n===== 处理实例: {instance['name']} =====")
        adb_port = instance["adb_port"]

        # 连接ADB
        final_port = connect_adb(adb_port)
        if not final_port:
            print(f"❌ ADB连接失败 (端口: {adb_port})")
            return False
        else:
            print(f"✅ ADB连接成功 (最终端口: {final_port})")
            instance["adb_port"] = final_port  # 更新实例的ADB端口
    return True

# ===== 主流程 =====
def main() -> bool:
    print("===== MuMu多开自动启动脚本 =====")
    # 尝试启动模拟器和游戏
    success = False
    for attempt in range(CONFIG["max_retries"]):
        print(f"尝试第 {attempt + 1} 次启动...")
        if activate_all_mumu():
            success = True
            break
        else:
            print("启动失败，正在重试...")
            kill_mumu_process()
            time.sleep(30)  # 等待一段时间后重试

    if not success:
        print("❌ 所有启动方式均失败，请检查配置！")
    return success


if __name__ == "__main__":
    main()  # 激活所有MuMu模拟器
