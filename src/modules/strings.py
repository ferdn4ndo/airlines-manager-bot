import re

from modules.logger import log, LogLevels


def sanitize_text(input_text) -> str:
    """
    Sanitizes a string parsed from HTML, removing extra spaces and newlines.
    :param input_text:
    :return:
    """
    log("Entering sanitize_text method", LogLevels.LOG_LEVEL_DEBUG)

    return re.sub(r'\s+', ' ', str(input_text).strip())


def return_only_numbers(input_text) -> int:
    """
    Retrieve only numbers (digits) from a given value
    :param input_text:
    :return:
    """
    log("Entering return_only_numbers method", LogLevels.LOG_LEVEL_DEBUG)

    numeric_string = re.sub(r'[^0-9]', '', str(input_text))

    return int(numeric_string) if numeric_string != '' else None
