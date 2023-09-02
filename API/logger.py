import sys
from datetime import datetime
from loguru import logger
import queue

LOG_PATH = r'./logs/log.log'

log_queue = queue.Queue()


def log_sink(message):
    record = message.record
    raw_date_str = record.get("time")
    raw_datetime = datetime.fromisoformat(str(raw_date_str))
    log_msg = (f'{str(raw_datetime)[0:19]}_{record.get("level")}_{record.get("module")}_{record.get("function")}：'
               f'{record.get("message")};')
    log_queue.put(log_msg)


logger.remove()

logger.add(log_sink, enqueue=True, level='INFO', format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}")
logger.add(sys.stderr, level='INFO', format="{time:YYYY-MM-DD HH:mm:ss}_{level}_{name}.{function}: {message}")
logger.add(LOG_PATH, level='DEBUG', format="{time:YYYY-MM-DD HH:mm:ss}  {level} {message}")
