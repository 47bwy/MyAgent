# -*- encoding: utf-8 -*-
'''
@Time    :   2025/05/22 10:12:47
@Author  :   47bwy
@Desc    :   日志
'''

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

# 日志目录路径
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 日志格式
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)


def _create_handler(level_name: str, file_name: str) -> RotatingFileHandler:
    """
    创建单个日志文件处理器，支持日志轮转
    """
    handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, file_name),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding="utf-8"
    )
    handler.setLevel(getattr(logging, level_name.upper()))
    handler.setFormatter(formatter)
    return handler


def setup_logging(console: bool = True):
    """
    初始化全局日志配置。仅需在 main.py 中调用一次。
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()  # 避免重复添加 handler

    # 按级别写入不同文件
    root_logger.addHandler(_create_handler("DEBUG", "debug.log"))
    root_logger.addHandler(_create_handler("INFO", "info.log"))
    root_logger.addHandler(_create_handler("ERROR", "error.log"))

    # 控制台输出（可选）
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取当前模块的 logger 实例（模块内用 __name__）
    """
    return logging.getLogger(name or __name__)
