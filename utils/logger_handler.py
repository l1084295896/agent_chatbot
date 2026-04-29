import logging
import os
from datetime import datetime
from utils.path_tool import get_abs_path


def setup_logger(
    name: str = "agent",
    level: int = logging.INFO,
    file_level: int = logging.INFO,
) -> logging.Logger:
    """配置日志记录器

    Args:
        name (str): 日志记录器名称,默认 agent
        level (int): 日志级别，默认 INFO
        file_level (int): 文件输出日志级别，默认 INFO

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 获取日志目录，不存在则创建
    log_dir = get_abs_path("logs")
    os.makedirs(log_dir, exist_ok=True)

    # 日志文件名格式：app_2026-04-27.log（按日期拆分）
    log_file = f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(log_dir, log_file)

    # 创建 logger 实例
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # 创建文件处理器，设置编码和日志级别
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setLevel(file_level)

        # 设置日志格式：时间 - 名称 - 级别 - 文件:行号 - 消息
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


if __name__ == "__main__":
    # 测试日志记录功能
    logger = setup_logger()
    logger.info("这是一条 info 日志")
    logger.warning("这是一条 warning 日志")
    logger.error("这是一条 error 日志")
    print(f"日志已写入 logs/app_{datetime.now().strftime('%Y-%m-%d')}.log")
