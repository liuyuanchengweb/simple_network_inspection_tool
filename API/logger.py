import sys
from loguru import logger

LOG_PATH = r'./logs/log.log'


def enqueue_log(message):
    pass


logger.remove()
logger.add(enqueue_log, enqueue=True, level='INFO', format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}")
logger.add(sys.stderr, level='INFO', format="{time:YYYY-MM-DD HH:mm:ss}  {level} {message}")
logger.add(LOG_PATH, level='DEBUG', format="{time:YYYY-MM-DD HH:mm:ss}  {level} {message}")
