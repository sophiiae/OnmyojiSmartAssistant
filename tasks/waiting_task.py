from typing import Union
from tasks.task_base import TaskBase
from module.control.server.device import Device
import time
from module.base.logger import logger

class WaitingTask(TaskBase):
    name = "WaitingTask"

    def __init__(self, device: Device) -> None:
        super().__init__(device)

    def run(self, duration_minutes: Union[float, None] = None):
        """
        运行等待任务
        :param duration_minutes: 运行时长（分钟），如果为None则使用默认的5分钟
        """
        if duration_minutes is None:
            duration_minutes = 5  # 默认5分钟

        # 将分钟转换为秒
        duration_seconds = duration_minutes * 60
        start_time = time.time()
        logger.info(
            f"⏳ 开始执行等待任务，将持续运行 {duration_minutes:.0f} 分钟...")

        while time.time() - start_time < duration_seconds:
            self.screenshot()
            # 检查邀请任务
            self.check_request_invitation()

            # 短暂休眠，避免过度占用CPU
            time.sleep(1)

            # 每分钟显示一次剩余时间
            elapsed = time.time() - start_time
            if int(elapsed) % 60 == 0:  # 每整分钟显示一次
                remaining = duration_seconds - elapsed
                if remaining > 0:
                    minutes = int(remaining // 60)
                    logger.info(f"剩余时间: {minutes} 分钟")

        logger.info("✅ 等待任务已完成")
