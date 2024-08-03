import re

from api.services import logging

class StringsService:

    def __init__(self):
        self.logger = logging.get_logger(__name__)

    def sanitize_text(self, input_text) -> str:
        """
        Sanitizes a string parsed from HTML, removing extra spaces and newlines.
        :param input_text:
        :return:
        """
        self.logger.debug("Entering sanitize_text method")

        return re.sub(r'\s+', ' ', str(input_text).strip())


    def return_only_numbers(self, input_text) -> int:
        """
        Retrieve only numbers (digits) from a given value
        :param input_text:
        :return:
        """
        self.logger.debug("Entering return_only_numbers method")

        numeric_string = re.sub(r'[^0-9]', '', str(input_text))

        return int(numeric_string) if numeric_string != '' else None
