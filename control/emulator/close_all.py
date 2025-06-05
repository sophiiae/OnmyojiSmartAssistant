import psutil

def kill_mumu_process(multi_only: bool = False):
    """强制结束所有MuMu模拟器进程"""
    processes = ['MuMuMultiPlayer.exe']
    if not multi_only:
        processes.append('MuMuPlayer.exe')

    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in processes:
            proc.kill()
            print(f"✅ 已终止进程: {proc.info['name']} (PID: {proc.pid})")


if __name__ == "__main__":
    print("正在关闭所有MuMu模拟器...")
    kill_mumu_process()
    print("所有MuMu模拟器已关闭。")
