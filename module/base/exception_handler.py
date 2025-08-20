"""
异常处理工具模块
提供更好的异常处理功能，避免异常导致整个OSA退出
"""

from module.base.logger import logger
from module.base.exception import (
    RequestHumanTakeover, TaskEnd, GamePageUnknownError,
    GameStuckError, GameNotRunningError, GameTooManyClickError,
    ScriptError, DeviceNotRunningError
)


class ExceptionHandler:
    """异常处理器，用于统一处理各种异常"""

    @staticmethod
    def handle_task_exception(exception: Exception, task_name: str = "Unknown") -> dict:
        """
        处理任务执行过程中的异常

        Args:
            exception: 捕获的异常
            task_name: 任务名称

        Returns:
            dict: 包含处理结果的字典
        """
        result = {
            "handled": True,
            "should_continue": True,
            "should_retry": False,
            "retry_delay": 0,
            "message": ""
        }

        if isinstance(exception, TaskEnd):
            # 正常任务结束
            result["message"] = f"任务 {task_name} 正常结束"
            result["should_continue"] = True
            logger.info(result["message"])

        elif isinstance(exception, RequestHumanTakeover):
            # 需要人工干预
            result["message"] = f"任务 {task_name} 需要人工干预: {exception}"
            result["should_continue"] = False
            result["should_retry"] = False
            logger.critical(result["message"])
            logger.critical("请检查游戏状态或配置设置")

        elif isinstance(exception, (GamePageUnknownError, GameStuckError, GameNotRunningError, GameTooManyClickError)):
            # 游戏相关错误
            result["message"] = f"任务 {task_name} 遇到游戏错误: {exception}"
            result["should_continue"] = True
            result["should_retry"] = True
            result["retry_delay"] = 60  # 1分钟后重试
            logger.error(result["message"])
            logger.error("任务将被标记为失败，但OSA将继续运行")

        elif isinstance(exception, ScriptError):
            # 脚本开发错误
            result["message"] = f"任务 {task_name} 遇到脚本错误: {exception}"
            result["should_continue"] = True
            result["should_retry"] = False
            logger.error(result["message"])
            logger.error("这可能是开发问题，任务将被标记为失败")

        elif isinstance(exception, DeviceNotRunningError):
            # 设备相关错误
            result["message"] = f"任务 {task_name} 遇到设备错误: {exception}"
            result["should_continue"] = True
            result["should_retry"] = True
            result["retry_delay"] = 120  # 2分钟后重试
            logger.error(result["message"])
            logger.error("请检查设备状态，任务将被标记为失败")

        else:
            # 其他未预期的异常
            result["message"] = f"任务 {task_name} 遇到未预期的错误: {exception}"
            result["should_continue"] = True
            result["should_retry"] = False
            logger.error(result["message"])
            logger.error(f"异常类型: {type(exception).__name__}")
            logger.error("任务将被标记为失败，但OSA将继续运行")

            # 记录完整的异常堆栈信息
            import traceback
            logger.error(f"完整异常堆栈:\n{traceback.format_exc()}")

            # 尝试获取当前配置名称
            try:
                from module.base.logger import get_current_config_name
                config_name = get_current_config_name()
                if config_name:
                    logger.error(f"配置文件: {config_name}.json")
            except:
                pass

        return result

    @staticmethod
    def log_exception_with_context(exception: Exception, context: str = "", include_traceback: bool = True):
        """
        记录异常信息，包含上下文信息

        Args:
            exception: 异常对象
            context: 上下文信息
            include_traceback: 是否包含堆栈跟踪
        """
        if context:
            logger.error(f"在 {context} 中发生异常: {exception}")
        else:
            logger.error(f"发生异常: {exception}")

        if include_traceback:
            import traceback
            logger.error(f"异常堆栈跟踪:\n{traceback.format_exc()}")

    @staticmethod
    def should_retry_task(exception: Exception, retry_count: int, max_retries: int = 3) -> bool:
        """
        判断是否应该重试任务

        Args:
            exception: 异常对象
            retry_count: 当前重试次数
            max_retries: 最大重试次数

        Returns:
            bool: 是否应该重试
        """
        if retry_count >= max_retries:
            return False

        # 某些异常类型不应该重试
        if isinstance(exception, (TaskEnd, RequestHumanTakeover, ScriptError)):
            return False

        # 游戏相关错误和设备错误可以重试
        if isinstance(exception, (GamePageUnknownError, GameStuckError, GameNotRunningError, GameTooManyClickError, DeviceNotRunningError)):
            return True

        return False


def safe_execute(func, *args, **kwargs):
    """
    安全执行函数的装饰器函数

    Args:
        func: 要执行的函数
        *args: 函数参数
        **kwargs: 函数关键字参数

    Returns:
        tuple: (success, result, exception)
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        return False, None, e


def retry_on_exception(func, max_retries: int = 3, retry_delay: float = 1.0,
                       retryable_exceptions: tuple | None = None):
    """
    在异常时重试函数的装饰器

    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        retryable_exceptions: 可重试的异常类型元组

    Returns:
        装饰后的函数
    """
    if retryable_exceptions is None:
        retryable_exceptions = (GamePageUnknownError, GameStuckError, GameNotRunningError,
                                GameTooManyClickError, DeviceNotRunningError)

    def wrapper(*args, **kwargs):
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt == max_retries:
                    logger.error(
                        f"函数 {func.__name__} 在 {max_retries + 1} 次尝试后仍然失败")
                    raise last_exception

                if isinstance(e, retryable_exceptions):
                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}")
                    logger.info(f"将在 {retry_delay} 秒后重试...")
                    import time
                    time.sleep(retry_delay)
                else:
                    # 不可重试的异常，直接抛出
                    raise e

        return None

    return wrapper
