"""
日志配置
"""
import os
import sys
from pathlib import Path
from loguru import logger

# 创建日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = os.getenv("LOG_FILE", "logs/ainews.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def setup_logger():
    """配置日志"""
    # 移除默认处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL,
        colorize=True
    )
    
    # 添加文件输出
    logger.add(
        LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=LOG_LEVEL,
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    return logger


def get_logger(name: str = None):
    """获取logger实例"""
    if name:
        return logger.bind(name=name)
    return logger


# 初始化
setup_logger()

