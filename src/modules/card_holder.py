import json
import os
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from requests.cookies import RequestsCookieJar
from typing import Dict

from .file import save_dict_to_json
from .logger import log, LogLevels, save_error_dump
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
    log("Free card holder results: {}".format(json.dumps(card_holder_result)))


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

    card_holder_title = card_holder_bs.find('div', attrs={'class': 'cardholder-title'})
    if card_holder_title is None:
        log("Aborting card hold opening as the page title was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump(dump=card_holder_response.text, tag='card_holder_title_div_not_found')
        raise ReferenceError("Div with class cardholder-title was not found")

    has_countdown = card_holder_bs.find('div', attrs={'id': 'timerFree'})
    log("Free Card Holder available: {}".format('NO' if has_countdown else 'YES'))

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

    parsed_results = parse_card_holder_bonuses(original_json_data['bonuses'])

    save_card_holder_results(parsed_results)

    return parsed_results


def parse_card_holder_bonuses(bonuses_response: str) -> Dict:
    """
    Parse the HTML response of the card holder into a dict
    :param bonuses_response:
    :return:
    """
    bonuses_response_bs = BeautifulSoup(bonuses_response, 'html.parser')

    bonuses_set = bonuses_response_bs.find_all('div', attrs={'class': 'cardholder-bonus-container'})
    parsed_bonuses = [parse_card_holder_bonus(bonus_bs) for bonus_bs in bonuses_set]

    return {
        'bonuses': parsed_bonuses,
        'total_bonuses': len(bonuses_set),
    }


def parse_card_holder_bonus(bonus_bs: BeautifulSoup) -> Dict:
    """
    Parse a single bonus element of BeautifulSoup type
    :param bonus_bs:
    :return:
    """
    image_bs = bonus_bs.find('img', attrs={'class': 'cardholder-bonus-image'})
    bonus_text_bs = bonus_bs.find('div', attrs={'class': 'cardholder-bonus-text'})

    return {
        'image_src': image_bs['src'] if image_bs is not None else '--Unknown--',
        'bonus_text': bonus_text_bs.get_text if bonus_text_bs is not None else '--Unknown--',
    }


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
