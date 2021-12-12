import os
import pickle
import requests

from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from .logger import log, LogLevels, save_error_dump
from .user_agent import get_base_headers


def get_cookies() -> RequestsCookieJar:
    """
    Retrieves the cookie jar to be used with authorized requests.
    :return:
    """
    if not check_cookies_file_sanity():
        return refresh_login_cookies(os.environ['AM_USER_EMAIL'], os.environ['AM_USER_PASSWORD'])

    return read_cookies_file()


def get_cookies_filepath() -> str:
    """
    Retrieve the path of the file to store the cookies
    :return:
    """
    return os.environ['COOKIES_FILEPATH'] if 'COOKIES_FILEPATH' in os.environ else '/data/cookies.dat'


def check_cookies_file_sanity() -> bool:
    """
    Determines if the stored cookies data is still valid on authorized requests.
    :return:
    """
    cookies = read_cookies_file()
    session = requests.Session()
    session.cookies.update(cookies)
    home_response = session.get(
        'https://tycoon.airlines-manager.com/home',
        headers=get_base_headers(),
        cookies=cookies,
        allow_redirects=False
    )
    session.close()

    cookies_are_ok = home_response.status_code == 200
    log("Current cookies status is {}".format("OK" if cookies_are_ok is True else "FAILING"))

    return cookies_are_ok


def refresh_login_cookies(email: str, password: str) -> RequestsCookieJar:
    """
    Refreshes the stored cookies by performing a new authentication with the user credentials.
    :param email:
    :param password:
    :return:
    """
    # Gets the CSRF token
    session = requests.Session()
    login_page_response = session.get('https://tycoon.airlines-manager.com/login', headers=get_base_headers())
    login_page_bs = BeautifulSoup(login_page_response.text, 'html.parser')

    csrf_token_field = login_page_bs.find('input', attrs={'name': '_csrf_token'})
    if csrf_token_field is None:
        log("The CSRF token field was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump(dump=login_page_response.text, tag='csrf_token_field_not_found')
        raise ReferenceError("The CSRF token field was not found")

    csrf_token = csrf_token_field['value']
    log("CSRF Token: {}".format(csrf_token))

    # Performs the login
    login_payload = {
        '_remember_me': 'off',
        '_username': email,
        '_password': password,
        '_csrf_token': csrf_token,
    }
    session.post(
        'https://tycoon.airlines-manager.com/login_check',
        data=login_payload,
        headers=get_base_headers()
    )
    save_cookies_file(session.cookies)

    session.close()

    return session.cookies


def read_cookies_file() -> RequestsCookieJar:
    """
    Reads the cookies data file into a RequestsCookieJar object to be used with authorized requests.
    :return:
    """
    with open(get_cookies_filepath(), 'rb') as cookies_file:
        cookies = pickle.load(cookies_file)

    return cookies


def save_cookies_file(cookies: RequestsCookieJar):
    """
    Saves the cookies data (from a RequestsCookieJar object) to the file.
    :param cookies:
    :return:
    """
    with open(get_cookies_filepath(), 'wb') as cookies_file:
        pickle.dump(cookies, cookies_file)
    log("Cookies saved!")
