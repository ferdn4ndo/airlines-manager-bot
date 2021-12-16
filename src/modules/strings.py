import re


def sanitize_text(input_text) -> str:
    """
    Sanitizes a string parsed from HTML, removing extra spaces and newlines.
    :param input_text:
    :return:
    """
    return re.sub(r'\s+', ' ', str(input_text).strip())


def return_only_numbers(input_text) -> int:
    """
    Retrieve only numbers (digits) from a given value
    :param input_text:
    :return:
    """
    numeric_string = re.sub(r'[^0-9]', '', str(input_text))

    return int(numeric_string) if numeric_string != '' else None
