import os
from datetime import datetime

from api.services import logging
from api.services.file import TextFileService


class ErrorDumpService:
    def __init__(self):
        self.logger = logging.get_logger(__name__)

    def save_error_dump_file(self, dump: str, tag: str = 'dump'):
        """
        Saves an error dump to a file
        :param dump:
        :param tag:
        :return:
        """
        self.logger.debug("Entering save_error_dump_file method")
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = '{}_{}.txt'.format(timestamp, tag)
        filepath = os.path.join(os.getenv('ERROR_DUMPS_FOLDER', '/data/error_dumps'), filename)

        text_file_service = TextFileService(filepath=filepath)
        text_file_service.save_text_to_file(dump)

        self.logger.info("Saved error dump to {}".format(filepath))
