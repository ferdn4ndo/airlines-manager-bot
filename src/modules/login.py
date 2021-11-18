import os
import pickle
import requests

from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from .user_agent import get_base_headers


def get_cookies() -> RequestsCookieJar:
    """
    Retrieves the cookie jar to be used with authorized requests.
    :return:
    """
    if not check_cookies_file_sanity():
        return refresh_login_cookies(os.environ['AM_USER_EMAIL'], os.environ['AM_USER_PASSWORD'])

    return read_cookies_file()


def check_cookies_file_sanity() -> bool:
    """
    Determines if the stored cookies data is still valid on authorized requests.
    :return:
    """
    if not os.path.isfile(os.environ['COOKIES_FILEPATH']):
        print("Cookies file not present! Path: {}".format(os.environ['COOKIES_FILEPATH']))
        return False

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
    print("Current cookies status is {}".format("OK" if cookies_are_ok is True else "FAILING"))

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
    csrf_token = login_page_bs.find('input', attrs={'name': '_csrf_token'})['value']
    print("CSRF Token: {}".format(csrf_token))

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
    with open(os.environ['COOKIES_FILEPATH'], 'rb') as cookies_file:
        cookies = pickle.load(cookies_file)

    return cookies


def save_cookies_file(cookies: RequestsCookieJar):
    """
    Saves the cookies data (from a RequestsCookieJar object) to the file.
    :param cookies:
    :return:
    """
    with open(os.environ['COOKIES_FILEPATH'], 'wb') as cookies_file:
        pickle.dump(cookies, cookies_file)
    print("Cookies saved!")
