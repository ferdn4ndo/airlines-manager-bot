import os

from datetime import datetime


class LogLevels:
    """
    Enum for the possible logging levels
    """
    LOG_LEVEL_DEBUG = 'debug'
    LOG_LEVEL_INFO = 'info'
    LOG_LEVEL_WARNING = 'warning'
    LOG_LEVEL_ERROR = 'error'


def log(message: str, level: str = LogLevels.LOG_LEVEL_INFO, append_newline=True):
    """
    Logs a message
    :param message:
    :param level:
    :param append_newline:
    :return:
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = '[{timestamp} {level}] {message}'.format(
        timestamp=timestamp,
        level=level.upper(),
        message=message,
    )
    with open(os.getenv('LOG_FILEPATH', '/data/log.txt'), 'a') as f:
        f.write((log_message + '\n') if append_newline else log_message)

    print(log_message)
