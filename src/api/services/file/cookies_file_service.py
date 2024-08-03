import os
import pickle

from requests.cookies import RequestsCookieJar

from api.services import logging

from .binary_file_service import BinaryFileService
from .file_mode import FileMode


class CookiesFileService:
    DEFAULT_COOKIES_FILEPATH = '/data/cookies.dat'

    def __init__(self):
        self.logger = logging.get_logger(__name__)
        self.filepath = os.getenv('COOKIES_FILEPATH', self.DEFAULT_COOKIES_FILEPATH)

    def read_cookies_file(self) -> RequestsCookieJar:
        """
        Reads the cookies data file into a RequestsCookieJar object to be used with authorized requests.
        :return:
        """
        self.logger.debug("Entering read_cookies_file method")

        binary_service = BinaryFileService(filepath=self.filepath)

        return binary_service.read_binary_file()


    def save_cookies_file(self, cookies: RequestsCookieJar):
        """
        Saves the cookies data (from a RequestsCookieJar object) to the file.
        :param cookies:
        :return:
        """
        self.logger.debug("Entering save_cookies_file method")
        with open(self.filepath, FileMode.FILE_MODE_WRITE + FileMode.FILE_MODE_BINARY) as cookies_file:
            pickle.dump(cookies, cookies_file)
