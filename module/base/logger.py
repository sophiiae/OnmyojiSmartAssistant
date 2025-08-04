import logging
import logging.config
import sys
# import os
from typing import Deque
from collections import deque
from datetime import datetime
from logging.handlers import RotatingFileHandler
import threading

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[41m',  # 红底
        'SUCCESS': '\033[92m',   # 亮绿色
        'SYSTEM': '\033[94m',    # 蓝色
        'NETWORK': '\033[95m',   # 紫色
        'AI': '\033[96m'         # 亮青色
    }
    RESET = '\033[0m'

    def format(self, record):
        # 先调用父类的format方法，确保asctime等属性被设置
        super().format(record)

        # 如果是后台消息，使用特殊格式
        if getattr(record, 'is_background', False):
            return f"[{record.asctime}] [BG] {record.getMessage()}"

        # 获取消息类型
        msg_type = getattr(record, 'msg_type', '')
        if msg_type in self.COLORS:
            color = self.COLORS[msg_type]
            return f"{color}[{record.asctime}] [{msg_type:<8}] {record.getMessage()}{self.RESET}"

        # 其他消息使用对应的颜色
        color = self.COLORS.get(record.levelname, '')
        message = super().format(record)
        return f"{color}{message}{self.RESET}"

class ContextFormatter(logging.Formatter):
    """带上下文的格式化器"""

    def format(self, record):
        # 确保context字段存在
        if not hasattr(record, 'context'):
            record.context = ''
        return super().format(record)


# 日志配置字典
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'console': {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s',
            'datefmt': '%H:%M:%S'
        },
        'file': {
            'format': '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]\n'
            '=== CONTEXT ===\n%(context)s\n'
            '=== MESSAGE ===\n%(message)s\n'
            '================',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'console',
            'stream': sys.stdout
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'file',
            'filename': 'logs/game_errors.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
            'encoding': 'utf-8'
        }
    },

    'loggers': {
        'GameConsole': {
            'handlers': ['console', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

class GameConsoleLogger:
    def __init__(self, debug_mode: bool = False):
        """初始化日志系统"""
        # os.makedirs('logs', exist_ok=True)

        # # 删除现有的日志文件
        # log_files = ['logs/game_debug.log', 'logs/game_errors.log']
        # for log_file in log_files:
        #     if os.path.exists(log_file):
        #         try:
        #             os.remove(log_file)
        #         except Exception as e:
        #             print(f"无法删除日志文件 {log_file}: {e}")

        # 动态调整控制台日志级别
        LOG_CONFIG['handlers']['console']['level'] = 'DEBUG' if debug_mode else 'INFO'

        # 应用配置
        logging.config.dictConfig(LOG_CONFIG)
        self.logger = logging.getLogger('GameConsole')
        self._context_buffer = deque(maxlen=20)

        # UI回调函数列表 - 支持多个回调，每个回调包含配置名称和回调函数
        self.ui_callbacks = []

        # 替换原error方法
        self._original_error = self.logger.error
        self.logger.error = self._enhanced_error

        # 清除已有处理器
        self.logger.handlers.clear()

        # 控制台Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        formatter = ColorFormatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 调试日志文件Handler - 仅在debug_mode为True时创建
        if debug_mode:
            debug_file_handler = RotatingFileHandler(
                'logs/game_debug.log',
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3,
                encoding='utf-8',
                mode='w'  # 使用 'w' 模式，每次创建新文件
            )
            debug_file_handler.setLevel(logging.DEBUG)
            debug_formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            debug_file_handler.setFormatter(debug_formatter)
            self.logger.addHandler(debug_file_handler)

        # 错误日志文件Handler
        error_file_handler = RotatingFileHandler(
            'logs/game_errors.log',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8',
            mode='w'  # 使用 'w' 模式，每次创建新文件
        )
        error_file_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]\n'
            '=== CONTEXT ===\n%(context)s\n'
            '=== MESSAGE ===\n%(message)s\n'
            '================',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_file_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_file_handler)

    def set_ui_callback(self, callback, config_name=None):
        """设置UI回调函数 - 支持按配置名称过滤"""
        if callback is None:
            # 如果传入None，清空所有回调
            self.ui_callbacks.clear()
        else:
            # 添加新的回调到列表，包含配置名称
            callback_info = {'callback': callback, 'config_name': config_name}
            if callback_info not in self.ui_callbacks:
                self.ui_callbacks.append(callback_info)

    def remove_ui_callback(self, callback):
        """移除特定的UI回调函数"""
        for callback_info in self.ui_callbacks[:]:
            if callback_info['callback'] == callback:
                self.ui_callbacks.remove(callback_info)

    def _notify_ui(self, message, config_name=None):
        """通知所有UI更新 - 支持按配置名称过滤"""
        if self.ui_callbacks:
            # 向所有匹配的回调发送消息
            for callback_info in self.ui_callbacks[:]:  # 使用副本避免在迭代时修改列表
                try:
                    # 如果回调没有指定配置名称，或者配置名称匹配，则发送消息
                    if (callback_info['config_name'] is None or
                        config_name is None or
                            callback_info['config_name'] == config_name):
                        callback_info['callback'](message)
                except Exception as e:
                    # 如果某个回调出错，移除它
                    print(f"UI callback error: {e}")
                    self.ui_callbacks.remove(callback_info)

    def _enhanced_error(self, msg, *args, **kwargs):
        """增强的错误记录"""
        kwargs.setdefault('extra', {})['context'] = '\n'.join(
            self._context_buffer)
        self._original_error(msg, *args, **kwargs)
        self._flush_handlers()

        # 获取配置名称
        config_name = kwargs.get('extra', {}).get('config_name', None)

        # 通知UI
        self._notify_ui(f"❌ {msg}", config_name)

    def _flush_handlers(self):
        for handler in self.logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()

    def _add_context(self, level: str, message: str):
        self._context_buffer.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] {level}: {message}"
        )

    def _log_with_context(self, level: str, msg: str, config_name=None, **kwargs):
        """带上下文的日志记录"""
        extra = kwargs.setdefault('extra', {})
        extra['context'] = '\n'.join(self._context_buffer)
        if 'msg_type' in kwargs:
            extra['msg_type'] = kwargs.pop('msg_type')
        if 'is_background' in kwargs:
            extra['is_background'] = kwargs.pop('is_background')

        # 添加配置名称到extra中
        if config_name:
            extra['config_name'] = config_name

        getattr(self.logger, level.lower())(msg, **kwargs)

        # 通知UI
        self._notify_ui(msg, config_name)

    def background(self, msg: str, config_name=None):
        """后台信息（默认颜色）"""
        self._add_context('BACKGROUND', msg)
        self._log_with_context('info', msg, config_name, is_background=True)

    def success(self, msg: str, config_name=None):
        """成功信息（亮绿色）"""
        self._add_context('SUCCESS', msg)
        self._log_with_context(
            'info', f"✅ {msg}", config_name, msg_type='SUCCESS')

    def system(self, msg: str, config_name=None):
        """系统信息（蓝色）"""
        self._add_context('SYSTEM', msg)
        self._log_with_context(
            'info', f"🖥️ {msg}", config_name, msg_type='SYSTEM')

    def network(self, msg: str, config_name=None):
        """网络信息（紫色）"""
        self._add_context('NETWORK', msg)
        self._log_with_context(
            'info', f"🌐 {msg}", config_name, msg_type='NETWORK')

    def ai(self, msg: str, config_name=None):
        """AI信息（亮青色）"""
        self._add_context('AI', msg)
        self._log_with_context('info', f"🤖 {msg}", config_name, msg_type='AI')

    def debug(self, msg: str, config_name=None):
        """调试信息（青色）"""
        self._add_context('DEBUG', msg)
        self._log_with_context('debug', f"🐛 {msg}", config_name)

    def info(self, msg: str, config_name=None):
        """一般信息（绿色）"""
        self._add_context('INFO', msg)
        self._log_with_context('info', f"ℹ️ {msg}", config_name)

    def warning(self, msg: str, config_name=None):
        """警告信息（黄色）"""
        self._add_context('WARNING', msg)
        self._log_with_context('warning', f"⚠️ {msg}", config_name)

    def error(self, msg: str, config_name=None, exc_info: bool = True):
        """错误信息（红色）- 同时写入文件"""
        self._add_context('ERROR', msg)
        self._log_with_context(
            'error', f"❌ {msg}", config_name, exc_info=exc_info)

    def critical(self, msg: str, config_name=None):
        """严重错误（红底）- 同时写入文件"""
        self._add_context('CRITICAL', msg)
        self._log_with_context('critical', f"💥 {msg}", config_name)


# 使用线程本地存储来管理配置名称
_thread_local = threading.local()

def set_current_config_name(config_name):
    """设置当前配置名称"""
    _thread_local.current_config_name = config_name

def get_current_config_name():
    """获取当前配置名称"""
    return getattr(_thread_local, 'current_config_name', None)

def clear_current_config_name():
    """清除当前配置名称"""
    if hasattr(_thread_local, 'current_config_name'):
        delattr(_thread_local, 'current_config_name')


# 创建logger实例
logger = GameConsoleLogger(debug_mode=False)

# 重写logger方法，自动获取当前配置名称
def _get_config_name_from_args(args):
    """从参数中获取配置名称"""
    if args and isinstance(args[0], str):
        # 如果第一个参数是字符串，可能是配置名称
        return args[0]
    return get_current_config_name()


# 重写logger的方法，自动传递配置名称
original_methods = {}

def _wrap_logger_method(method_name):
    """包装logger方法，自动传递配置名称"""
    original_method = getattr(logger, method_name)

    def wrapped_method(msg, *args, **kwargs):
        # 检查是否已经传递了配置名称
        if 'config_name' not in kwargs:
            # 从线程本地存储获取配置名称
            config_name = get_current_config_name()
            if config_name:
                kwargs['config_name'] = config_name
        return original_method(msg, *args, **kwargs)

    return wrapped_method


# 重写所有logger方法
for method_name in ['info', 'warning', 'error', 'critical', 'debug', 'success', 'system', 'network', 'ai', 'background']:
    original_methods[method_name] = getattr(logger, method_name)
    setattr(logger, method_name, _wrap_logger_method(method_name))

# 使用示例
if __name__ == "__main__":
    # 测试不同类型的日志
    logger.info("游戏启动")
    logger.success("成功加载配置文件")
    logger.system("系统初始化完成")
    logger.network("连接到游戏服务器")
    logger.ai("AI模型加载完成")
    logger.background("内存使用: 45%")
    logger.debug("玩家坐标: (120, 80)")
    logger.warning("网络延迟较高")

    try:
        raise RuntimeError("测试错误")
    except Exception as e:
        logger.error(f"发生错误: {e}")
        logger.critical("游戏即将退出")
