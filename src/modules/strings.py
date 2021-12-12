import re


def sanitize_text(input_text) -> str:
    """
    Sanitizes a string parsed from HTML, removing extra spaces and newlines.
    :param input_text:
    :return:
    """
    return re.sub(r'\s+', ' ', str(input_text).strip())
