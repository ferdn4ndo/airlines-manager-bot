import json
import os
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from requests.cookies import RequestsCookieJar
from typing import Dict

from .common import save_dict_to_json
from .user_agent import get_base_headers


def get_free_card_holder_if_available(cookies: RequestsCookieJar):
    """
    Checks if the free Card Holder is available, and open it if so
    :param cookies:
    :return:
    """
    if not is_free_card_holder_available(cookies):
        return

    card_holder_result = open_free_card_holder(cookies)
    print("Free Card Holder Results:")
    print(card_holder_result)


def is_free_card_holder_available(cookies: RequestsCookieJar) -> bool:
    """
    Determines if the free Card Holder is available to open
    :param cookies:
    :return:
    """
    card_holder_response = requests.get(
        'https://tycoon.airlines-manager.com/shop/cardholder',
        headers=get_base_headers({
            'Referer': 'https://tycoon.airlines-manager.com/home',
        }),
        cookies=cookies,
    )
    card_holder_bs = BeautifulSoup(card_holder_response.text, 'html.parser')
    has_countdown = card_holder_bs.find('div', attrs={'id': 'timerFree'})

    print("Free Card Holder available: {}".format("NO" if has_countdown else "YES"))

    return not has_countdown


def open_free_card_holder(cookies: RequestsCookieJar) -> Dict:
    """
    Opens the free Card Holder, save and return the results (must check if available first!)
    :param cookies:
    :return:
    """
    free_card_holder_response = requests.get(
        'https://tycoon.airlines-manager.com/shop/cardholder/cards',
        headers=get_base_headers({
            'Accept': '*/*',
            'Referer': 'https://tycoon.airlines-manager.com/shop/cardholder',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept-Language': 'en-US,en;q=0.9',
        }),
        cookies=cookies,
    )

    original_json_data = json.loads(free_card_holder_response.text)

    parsed_results = {
        'bonuses': original_json_data['bonuses'],
    }

    save_card_holder_results(parsed_results)

    return parsed_results


def save_card_holder_results(parsed_results: Dict):
    """
    Saves the free Card Holder results to a json file
    :param parsed_results:
    :return:
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = 'card_holder_results__{}.json'.format(timestamp)
    filepath = os.path.join(os.environ['CARD_HOLD_RESULTS_FOLDER'], filename)

    save_dict_to_json(parsed_results, filepath)
