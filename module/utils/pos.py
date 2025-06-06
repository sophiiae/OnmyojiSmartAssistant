import pyautogui

print("按 Ctrl+C 或关闭窗口退出...")
try:
    while True:
        x, y = pyautogui.position()  # 获取鼠标坐标
        rgb = pyautogui.screenshot().getpixel((x, y))  # 获取当前像素颜色
        print(f"X: {x}, Y: {y}, RGB: {rgb}", end="\r")  # 实时打印坐标
except KeyboardInterrupt:
    print("\n已退出坐标检测模式")
