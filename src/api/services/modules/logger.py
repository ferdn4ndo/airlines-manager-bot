import os

from datetime import datetime


class LogLevels:
    """
    Enum for the possible logging levels
    """
    LOG_LEVEL_DEBUG = 'debug'
    LOG_LEVEL_NOTICE = 'notice'
    LOG_LEVEL_INFO = 'info'
    LOG_LEVEL_WARNING = 'warning'
    LOG_LEVEL_ERROR = 'error'
    LOG_LEVEL_NONE = 'none'

    LOG_WEIGHTS = {
        LOG_LEVEL_DEBUG: 5,
        LOG_LEVEL_NOTICE: 4,
        LOG_LEVEL_INFO: 3,
        LOG_LEVEL_WARNING: 2,
        LOG_LEVEL_ERROR: 1,
        LOG_LEVEL_NONE: 0,
    }


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

    logs_folder = os.getenv('LOGS_FOLDER', '/data/logs')
    os.makedirs(logs_folder, exist_ok=True)

    log_filename = 'log_{}.txt'.format(datetime.now().strftime('%Y-%m-%d'))
    log_filepath = os.path.join(logs_folder, log_filename)

    with open(log_filepath, 'a') as f:
        f.write((log_message + '\n') if append_newline else log_message)

    if should_print_log_level(level=level):
        print(log_message)

def should_print_log_level(level: str) -> bool:
    """
    Determines if a given log level should be printed (lower or equal to the one set in the environment)
    :param level:
    :return:
    """
    env_log_level = os.getenv('LOG_LEVEL', LogLevels.LOG_LEVEL_INFO)
    env_log_level_weight = LogLevels.LOG_WEIGHTS[env_log_level] if env_log_level in LogLevels.LOG_WEIGHTS else 5
    message_log_level_weight = LogLevels.LOG_WEIGHTS[level] if level in LogLevels.LOG_WEIGHTS else 0

    return message_log_level_weight <= env_log_level_weight

