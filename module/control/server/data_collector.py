
from datetime import datetime
import time
from pathlib import Path
import cv2
import os

from module.control.server.device import Device
from module.base.logger import logger
# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# 数据相关配置
DATA_DIR = PROJECT_ROOT / "data"
LABELED_DATA_DIR = DATA_DIR / "labeled_data"
MODELS_DIR = DATA_DIR / "models"
VIDEOS_DIR = DATA_DIR / "videos"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"


class DataCollector(Device):
    """数据收集器，用于收集阴阳师游戏画面"""

    def __init__(self, config_name: str):
        super().__init__(config_name)
        # self.output_dir = Path(output_dir) if output_dir else DATA_DIR
        # self.output_dir.mkdir(exist_ok=True)

    def capture_screenshots(self, duration=60, interval=0.5):
        """从模拟器收集连续截图数据"""
        if not self.device:
            logger.error("模拟器未连接，请先调用 connect_emulator()")
            return 0

        start_time = time.time()
        count = 0

        while time.time() - start_time < duration:
            got_image = self.capture_screenshot(SCREENSHOTS_DIR)
            if got_image:
                count += 1
            time.sleep(interval)

        logger.info(f"模拟器截图收集完成，共收集 {count} 张图像")
        return count

    def record_video(self, duration=60, output_path=None):
        if not self.device:
            logger.error("模拟器未连接，请先调用 connect_emulator()")
            return None

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = VIDEOS_DIR / f"recording_{timestamp}.mp4"

        try:
            print(f"开始录制视频，时长: {duration} 秒")
            print("使用模拟器原始清晰度录制")

            # 使用AdbClient执行screenrecord命令，不限制分辨率
            result = self.device.shell(
                f'screenrecord --time-limit {duration} '
                f'--bit-rate 8000000 '  # 提高比特率到8Mbps
                f'/sdcard/screen_record.mp4'
            )

            if result.strip() == "":
                # 录制完成，开始下载文件
                print("录制完成，正在下载视频文件...")

                # 使用AdbClient下载文件 - 修复参数
                self.device.pull('/sdcard/screen_record.mp4', output_path)

                # 清理设备上的临时文件
                self.device.shell('rm /sdcard/screen_record.mp4')

                print(f"视频录制完成: {output_path}")
            else:
                print(f"录制失败: {result}")

        except Exception as e:
            print(f"录制过程中出现错误: {e}")

    def extract_from_video(self, video_path, output_interval=1.0):
        """从视频文件收集帧"""
        video_path = Path(video_path)
        if not video_path.exists():
            logger.error(f"视频文件不存在: {video_path}")
            return 0

        # 使用视频文件名作为文件夹名
        video_filename = os.path.splitext(os.path.basename(video_path))[0]
        output_dir = os.path.join(SCREENSHOTS_DIR, video_filename)

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * output_interval)

        count = 0
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                # 生成文件名（6位数字，从000000开始）
                frame_filename = f"frame_{count:06d}.jpg"
                frame_path = os.path.join(output_dir, frame_filename)

                # 保存帧图像，保持原始质量
                cv2.imwrite(frame_path, frame, [
                            cv2.IMWRITE_JPEG_QUALITY, 100])
                count += 1

                # 显示进度
                if count % 10 == 0 or frame_count == frame_count - 1:
                    progress = (frame_count / frame_count) * 100
                    print(
                        f"  - 已处理 {frame_count}/{frame_count} 帧，提取 {count} 帧 ({progress:.1f}%)")

            frame_count += 1

        cap.release()
        logger.info(f"从视频收集完成，共收集 {count} 张图像")
        return output_dir


if __name__ == "__main__":
    import sys
    # example:  py -m module.control.server.data_collector 1qian 90
    name, duration = sys.argv[1:]
    d = DataCollector(config_name=name)
    if len(sys.argv) < 3:
        logger.error("Missing config name or save file name or type")
        logger.warning(
            "Format: py ./record.py [config_name] [duration(s)]")
    else:
        if not duration:
            logger.error("Missing duration for recording")
        else:
            d.record_video(int(duration))
