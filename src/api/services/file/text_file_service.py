import os

from api.services import logging

from .file_mode import FileMode
from .binary_file_service import BinaryFileService


class TextFileService(BinaryFileService):
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self.logger = logging.get_logger(__name__)

    def save_text_to_file(self, input_text: str, file_mode: str = FileMode.FILE_MODE_WRITE):
        """
        Saves a raw text input to a file
        :param input_text:
        :param file_mode:
        :return:
        """
        self.logger.debug("Entering save_text_to_file method")
        folder = os.path.dirname(self.filepath)
        os.makedirs(folder, exist_ok=True)

        with open(self.filepath, file_mode) as f:
            f.write(input_text)

    def read_text_file(self, file_mode: str = FileMode.FILE_MODE_READ):
        """
        Reads a file to a string
        :param file_mode:
        :return:
        """
        self.logger.debug("Entering read_text_file method")

        self.check_if_file_exists()

        with open(self.filepath, file_mode) as f:
            data = f.read()

        return data
