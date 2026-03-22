import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger("AlumniETL")
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
    logger.setLevel(logging.DEBUG) # 允许记录的最细级别

    # 创建格式器：时间 - 名字 - 级别 - 消息
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')

    # 1. 控制台处理器：显示 INFO 及以上信息
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 2. 文件处理器：记录所有 DEBUG 信息，且自动滚动（防止文件过大）
    file_handler = RotatingFileHandler("app_debug.log", maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

