import os
import requests

from bs4 import BeautifulSoup
from typing import Dict

from modules.file import save_cookies_file, read_cookies_file, save_error_dump_file
from modules.logger import log, LogLevels
from modules.time import wait_random_interval
from modules.user_agent import get_random_user_agent


class SessionManager:
    """
    Class used to handle the sessions for making requests in an authorized environment
    """
    _session = None
    _user_agent = None

    class Methods:
        """
        Enum class for the HTTP methods
        """
        GET = 'get'
        POST = 'post'
        PATCH = 'patch'
        DELETE = 'delete'
        OPTIONS = 'options'


    def get_session(self) -> requests.Session:
        """
        Retrieve the session object to use on the requests (will create and authenticate one if not present)
        :return:
        """
        log("Entering get_session method", LogLevels.LOG_LEVEL_DEBUG)

        if self._session is not None:
            return self._session

        self._session = requests.Session()

        log("A new session was created, checking cookies", LogLevels.LOG_LEVEL_NOTICE)
        cookies_are_ok = self.check_cookies_file_sanity()
        if not cookies_are_ok:
            email = os.environ['AM_USER_EMAIL']
            password = os.environ['AM_USER_PASSWORD']
            self.refresh_login_cookies(email=email, password=password)

        return self._session


    def get_user_agent(self) -> str:
        """
        Retrieve the user-agent to use on the requests (will select a random one if none is set)
        :return:
        """
        log("Entering get_user_agent method", LogLevels.LOG_LEVEL_DEBUG)

        if self._user_agent is not None:
            return self._user_agent

        self._user_agent = get_random_user_agent()
        log(f"Session user-agent updated to '{self._user_agent}'")


    def get_headers(self, extra_headers = None) -> Dict:
        """
        Retrieve the headers to use on the request (may be extended using the argument)
        :param extra_headers:
        :return:
        """
        log("Entering get_headers method", LogLevels.LOG_LEVEL_DEBUG)
        default_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'User-Agent': self.get_user_agent(),
        }

        if extra_headers is None:
            return default_headers

        return dict(default_headers, **extra_headers)


    def request(
            self,
            url: str,
            method: str = Methods.GET,
            extra_headers = None,
            payload = None,
            allow_redirects = True
    ):
        """
        Performs a request using the stored session
        :param url:
        :param method:
        :param extra_headers:
        :param payload:
        :param allow_redirects:
        :return:
        """
        log("Entering request method", LogLevels.LOG_LEVEL_DEBUG)
        session = self.get_session()

        if not hasattr(session, method):
            log(f"Invalid method '{method}' to request URL {url}!", LogLevels.LOG_LEVEL_ERROR)
            raise ValueError(f"Invalid method {method}")

        headers = self.get_headers(extra_headers)
        request_function = getattr(session, method)
        response = request_function(url=url, data=payload, headers=headers, allow_redirects=allow_redirects)

        save_cookies_file(response.cookies)

        wait_random_interval(
            wait_time_min=os.getenv('REQUEST_INTERVAL_MIN', 1),
            wait_time_max=os.getenv('REQUEST_INTERVAL_MAX', 5),
            log_output=False,
        )

        return response


    def check_cookies_file_sanity(self) -> bool:
        """
        Determines if the stored cookies data is still valid on authorized requests.
        :return:
        """
        log("Entering check_cookies_file_sanity method", LogLevels.LOG_LEVEL_DEBUG)

        cookies = read_cookies_file()
        self._session.cookies.update(cookies)

        home_response = self._session.get(
            url='http://tycoon.airlines-manager.com/home',
            headers=self.get_headers(),
            allow_redirects=False
        )

        cookies_are_ok = home_response.status_code == 200
        log("Current cookies status is {}".format("OK" if cookies_are_ok is True else "FAILING"))

        return cookies_are_ok


    def refresh_login_cookies(self, email: str, password: str):
        """
        Refreshes the stored cookies by performing a new authentication with the user credentials.
        :param email:
        :param password:
        :return:
        """
        log("Entering refresh_login_cookies method", LogLevels.LOG_LEVEL_DEBUG)

        # Gets the CSRF token
        login_page_response = self._session.get(
            url='http://tycoon.airlines-manager.com/login',
            headers=self.get_headers(),
        )
        login_page_bs = BeautifulSoup(login_page_response.text, 'html.parser')

        csrf_token_field = login_page_bs.find('input', attrs={'name': '_csrf_token'})
        if csrf_token_field is None:
            log("The CSRF token field was not found!", LogLevels.LOG_LEVEL_ERROR)
            save_error_dump_file(dump=login_page_response.text, tag='csrf_token_field_not_found')
            raise ReferenceError("The CSRF token field was not found")

        csrf_token = csrf_token_field['value']
        log("CSRF Token: {}".format(csrf_token), LogLevels.LOG_LEVEL_NOTICE)

        # Performs the login
        login_payload = {
            '_remember_me': 'off',
            '_username': email,
            '_password': password,
            '_csrf_token': csrf_token,
        }
        login_check_response = self._session.post(
            url='http://tycoon.airlines-manager.com/login_check',
            data=login_payload,
        )
        log(f"Finished refreshing auth session ({len(login_check_response.text)} bytes retrieved)!")
