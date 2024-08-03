import os
import pickle

from api.services import logging

from .file_mode import FileMode


class BinaryFileService:
    def __init__(self, filepath: str):
        self.logger = logging.get_logger(__name__)
        self.filepath = filepath

    def check_if_file_exists(self):
        """
        Check if a given filepath exists and raise a FileNotFoundError if not
        :return:
        """
        self.logger.debug("Entering check_if_file_exists method")
        if not os.path.isfile(self.filepath):
            self.logger.error(f"Unable to locate file {self.filepath}!")
            raise FileNotFoundError(f"Unable to locate file {self.filepath}!")

    def read_binary_file(self, file_mode: str = FileMode.FILE_MODE_READ + FileMode.FILE_MODE_BINARY):
        """
        Reads a file to a string
        :param file_mode:
        :return:
        """
        self.logger.debug("Entering read_binary_file method")
        self.check_if_file_exists()

        with open(self.filepath, file_mode) as f:
            data = pickle.load(f)

        return data
