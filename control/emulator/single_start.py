import os
import subprocess
import sys
import time
import psutil

DEFAULT_ADB_PORT = 16384  # 默认ADB端口
x = 955  # 点击坐标X
y = 333  # 点击坐标Y

def start_mumu12():
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

    # MuMu12安装路径（请根据你的实际安装路径修改）
    mumu_path = r"C:\Program Files\Netease\MuMu Player 12\shell\MuMuPlayer.exe"

    if not os.path.exists(mumu_path):
        print(f"未找到MuMu12模拟器，请确认安装路径是否正确: {mumu_path}")
        return False

    # 启动MuMu12模拟器
    try:
        print("正在启动MuMu12模拟器...")
        subprocess.Popen([mumu_path])
        time.sleep(10)  # 等待模拟器启动完成
        return True
    except Exception as e:
        print(f"启动MuMu12模拟器时出错: {e}")
        return False

def connect_adb(port: int = DEFAULT_ADB_PORT) -> int:
    """连接ADB"""
    try:
        print(f"🔌 连接 ADB {port}...")
        for i in range(3):  # 尝试3次连接
            p = port + i
            result = subprocess.run(
                ["adb", "connect", f"127.0.0.1:{p}"],
                check=True,
                stdout=subprocess.PIPE,
            )
            if "connected to" in result.stdout.decode():
                print(f"✅ ADB {p} 连接成功！")
                return p
        else:
            print("❌ ADB 连接失败，请检查 MuMu12 是否开启 ADB 调试！")
            return None
    except:
        print("❌ ADB 连接失败，请检查 MuMu12 是否开启 ADB 调试！")
        return None

def start_onmyoji():
    """使用 ADB 启动阴阳师"""
    cmd = f"adb -s 127.0.0.1:{DEFAULT_ADB_PORT} shell input tap {x} {y}"

    try:
        print("🎮 启动阴阳师...")
        subprocess.run(cmd, shell=True, check=True)
        time.sleep(10)  # 等待游戏启动
        return True
    except subprocess.CalledProcessError:
        print("❌ 启动阴阳师失败，请检查包名和 Activity 是否正确！")
        return False


def check_mumu_process():
    """检查MuMu模拟器是否正在运行"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in ['MuMuPlayer.exe', 'MuMuMultiPlayer.exe']:
            return True
    return False


if __name__ == "__main__":
    if start_mumu12() and connect_adb() and start_onmyoji():
        print("✅ 阴阳师已启动！")
    else:
        print("❌ 启动失败，请检查错误信息！")
