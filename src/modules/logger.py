import os

from datetime import datetime

from .file import save_text_to_file, FileMode


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
    save_text_to_file(
        input_text=(log_message + '\n') if append_newline else log_message,
        output_filepath=os.environ['LOG_FILEPATH'],
        file_mode=FileMode.FILE_MODE_APPEND,
    )

    print(log_message)


def save_error_dump(dump: str, tag: str = 'dump'):
    """
    Saves an error dump to a file
    :param dump:
    :param tag:
    :return:
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = '{}_{}.txt'.format(timestamp, tag)
    filepath = os.path.join(os.environ['ERROR_DUMPS_FOLDER'], filename)
    save_text_to_file(dump, filepath)
    log("Saved error dump to {}".format(filepath))
