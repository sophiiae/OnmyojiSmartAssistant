from logger import GameConsoleLogger
import time
from typing import Callable, TypeVar, Optional, Any
from functools import wraps

T = TypeVar('T')

def retry(
    max_attempts: int = 3,
    timeout_seconds: float = 30.0,
    delay_seconds: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_failure: Optional[Callable[[int, float], Any]] = None,
    logger: Optional[GameConsoleLogger] = None
):
    """
    重试装饰器，为函数添加自动重试逻辑

    参数:
        max_attempts: 最大尝试次数 (默认: 3)
        timeout_seconds: 最大总超时时间(秒) (默认: 30)
        delay_seconds: 每次重试之间的延迟(秒) (默认: 1)
        exceptions: 触发重试的异常类型元组 (默认: 所有异常)
        on_failure: 所有尝试失败后的回调函数 (接收尝试次数和耗时)
        logger: 日志记录器实例
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.time()  # 记录开始时间
            attempt = 0               # 尝试次数计数器
            last_exception = None    # 记录最后一次异常

            # 重试循环：在最大尝试次数和超时时间内循环
            while attempt < max_attempts and (time.time() - start_time) < timeout_seconds:
                attempt += 1
                try:
                    # 尝试执行被装饰的函数
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    # 计算剩余时间
                    remaining_time = timeout_seconds - \
                        (time.time() - start_time)

                    # 记录错误日志
                    if logger:
                        logger.warning(
                            f"函数 {func.__name__} 执行失败 (尝试 {attempt}/{max_attempts}): {str(e)}"
                        )

                    # 如果还有重试机会且剩余时间足够，则延迟后重试
                    if attempt < max_attempts and remaining_time > delay_seconds:
                        if logger:
                            logger.info(
                                f"将在 {min(delay_seconds, remaining_time):.1f} 秒后重试...")
                        time.sleep(min(delay_seconds, remaining_time))

            # 所有尝试失败后的回调
            if on_failure is not None:
                on_failure(attempt, time.time() - start_time)

            # 记录最终失败日志
            if logger:
                if last_exception is not None:
                    logger.error(
                        f"函数 {func.__name__} 在 {attempt} 次尝试后仍然失败，"
                        f"总耗时 {time.time() - start_time:.1f} 秒"
                    )
                else:
                    logger.error(
                        f"函数 {func.__name__} 超时，"
                        f"耗时 {time.time() - start_time:.1f} 秒 (最大允许 {timeout_seconds} 秒)"
                    )

            # 抛出最后一次异常或超时错误
            if last_exception is not None:
                raise type(last_exception)(
                    f"操作在{attempt}次尝试后失败，总耗时{time.time() - start_time:.1f}秒。最后错误: {last_exception}"
                ) from last_exception
            raise TimeoutError(
                f"操作超时，耗时{time.time() - start_time:.1f}秒 (最大允许{timeout_seconds}秒)"
            )
        return wrapper
    return decorator


# 测试代码
if __name__ == "__main__":
    logger = GameConsoleLogger(debug_mode=True)

    # 测试重试装饰器
    @retry(
        max_attempts=3,
        timeout_seconds=10.0,
        delay_seconds=1.0,
        logger=logger
    )
    def test_retry_function(success_on_attempt: int) -> str:
        """测试函数，在指定尝试次数后成功"""
        global attempt_count
        attempt_count += 1

        if attempt_count < success_on_attempt:
            raise RuntimeError(f"模拟失败 (尝试 {attempt_count})")
        return f"成功完成 (尝试 {attempt_count})"

    # 测试场景1：第一次就成功
    logger.info("测试场景1：第一次就成功")
    attempt_count = 0
    try:
        result = test_retry_function(1)
        logger.success(result)
    except Exception as e:
        logger.error(f"测试失败: {e}")

    # 测试场景2：第二次成功
    logger.info("\n测试场景2：第二次成功")
    attempt_count = 0
    try:
        result = test_retry_function(2)
        logger.success(result)
    except Exception as e:
        logger.error(f"测试失败: {e}")

    # 测试场景3：第三次成功
    logger.info("\n测试场景3：第三次成功")
    attempt_count = 0
    try:
        result = test_retry_function(3)
        logger.success(result)
    except Exception as e:
        logger.error(f"测试失败: {e}")

    # 测试场景4：全部失败
    logger.info("\n测试场景4：全部失败")
    attempt_count = 0
    try:
        result = test_retry_function(4)  # 需要4次尝试，但只设置了3次重试
        logger.success(result)
    except Exception as e:
        logger.error(f"测试失败: {e}")

    # 测试场景5：超时
    logger.info("\n测试场景5：超时")
    attempt_count = 0
    try:
        result = test_retry_function(5)  # 需要5次尝试，但设置了3秒超时
        logger.success(result)
    except Exception as e:
        logger.error(f"测试失败: {e}")
