import json
import os

from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict

from .file import save_dict_to_json, save_error_dump_file
from .logger import log, LogLevels
from .session_manager import SessionManager
from .strings import sanitize_text


def get_free_card_holder_if_available(session_manager: SessionManager):
    """
    Checks if the free Card Holder is available, and open it if so
    :param session_manager:
    :return:
    """
    if not is_free_card_holder_available(session_manager=session_manager):
        return

    card_holder_result = open_free_card_holder(session_manager=session_manager)
    log("Free card holder results: {}".format(json.dumps(card_holder_result)))


def is_free_card_holder_available(session_manager: SessionManager) -> bool:
    """
    Determines if the free Card Holder is available to open
    :param session_manager:
    :return:
    """
    card_holder_response = session_manager.request(
        url='http://tycoon.airlines-manager.com/shop/cardholder',
        method=SessionManager.Methods.GET,
        extra_headers={
            'Referer': 'http://tycoon.airlines-manager.com/home',
        },
    )
    card_holder_bs = BeautifulSoup(card_holder_response.text, 'html.parser')

    card_holder_title = card_holder_bs.find('div', attrs={'class': 'cardholder-title'})
    if card_holder_title is None:
        log("Aborting card hold opening as the page title was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=card_holder_response.text, tag='card_holder_title_div_not_found')
        raise ReferenceError("Div with class cardholder-title was not found")

    has_countdown = card_holder_bs.find('div', attrs={'id': 'timerFree'})
    log("Free Card Holder available: {}".format('NO' if has_countdown else 'YES'))

    return not has_countdown


def open_free_card_holder(session_manager: SessionManager) -> Dict:
    """
    Opens the free Card Holder, save and return the results (must check if available first!)
    :param session_manager:
    :return:
    """
    card_holder_page_response = session_manager.request(
        url='http://tycoon.airlines-manager.com/shop/cardholder',
        method=SessionManager.Methods.GET,
        extra_headers={
            'Referer': 'http://tycoon.airlines-manager.com/home',
        },
    )
    log(f'Card holder page response got {len(card_holder_page_response.text)} bytes!')

    # ToDo: Discover how to find the localized URL from the previous page
    free_card_url = 'http://tycoon.airlines-manager.com/shop/buycards/5/0/Econ%C3%B4mica'

    free_card_holder_modal_response = session_manager.request(
        url=free_card_url,
        method=SessionManager.Methods.GET,
        extra_headers={
            'Accept': '*/*',
            'Authority': 'tycoon.airlines-manager.com',
            'Referer': 'http://tycoon.airlines-manager.com/shop/cardholder',
            'X-Requested-With': 'XMLHttpRequest',
        },
    )
    log(f'Free card holder modal response got {len(free_card_holder_modal_response.text)} bytes!')

    free_card_holder_modal_response_bs = BeautifulSoup(free_card_holder_modal_response.text, 'html.parser')
    free_card_csrf_token_input = free_card_holder_modal_response_bs.find('input', attrs={'id': 'form__token'})
    free_card_form_id_input = free_card_holder_modal_response_bs.find('input', attrs={'id': 'form_id'})

    csrf_token_value = free_card_csrf_token_input['value']
    form_id_value = free_card_form_id_input['value']
    free_card_opening_payload = {
        'form[id]': form_id_value,
        'form[_token]': csrf_token_value,
    }

    free_card_holder_opening_response = session_manager.request(
        url=free_card_url,
        method=SessionManager.Methods.POST,
        payload=free_card_opening_payload,
        extra_headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': free_card_url,
            'X-Requested-With': 'XMLHttpRequest',
        },
    )
    log(f'Free card holder opening response got {len(free_card_holder_opening_response.text)} bytes!')

    parsed_results = parse_card_holder_bonuses(free_card_holder_opening_response.text)

    save_card_holder_results(parsed_results)

    return parsed_results


def parse_card_holder_bonuses(card_holder_response: str) -> Dict:
    """
    Parse the HTML response of the card holder into a dict
    :param card_holder_response:
    :return:
    """
    bonuses_response_bs = BeautifulSoup(card_holder_response, 'html.parser')

    bonus_container = bonuses_response_bs.find('div', attrs={'id': 'bonusCards-container'})
    if bonus_container is None:
        log("Aborting card hold opening as the bonus response div was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=bonuses_response_bs.text, tag='card_holder_bonuses_div_not_found')
        raise ReferenceError("Div with class bonusCards-container was not found")

    bonuses_divs = bonus_container.find_all('div', attrs={'class': 'showCards-card front-card'})
    parsed_bonuses = [parse_card_holder_bonus(bonus_bs) for bonus_bs in bonuses_divs]

    return {
        'bonuses': parsed_bonuses,
        'total_bonuses': len(bonuses_divs),
    }


def parse_card_holder_bonus(bonus_bs: BeautifulSoup) -> Dict:
    """
    Parse a single bonus element of BeautifulSoup type
    :param bonus_bs:
    :return:
    """
    bonus_div = bonus_bs.find('div', attrs={'class': 'front-side-title textFill'})
    if bonus_div is None:
        log("Aborting card hold opening as the bonus div was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=bonus_bs.text, tag='card_holder_bonus_div_not_found')
        raise ReferenceError("Div not found in the bonus card container")

    bonus_image = bonus_div.find('img')
    if bonus_image is None:
        log("Aborting card hold opening as the bonus image was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=bonus_bs.text, tag='card_holder_bonus_img_not_found')
        raise ReferenceError("Image not found in the bonus card container")

    bonus_image_src = bonus_image['src']
    bonus_type = get_bonus_type_from_image_src(bonus_image_src)
    bonus_text = sanitize_text(bonus_div.string)

    return {
        'bonus_type': bonus_type,
        'bonus_text': bonus_text,
    }


def get_bonus_type_from_image_src(bonus_image_src: str):
    """
    Retrieve the type of the bonus based on the bonus image source
    :param bonus_image_src:
    :return:
    """
    image_src_parts = bonus_image_src.split('/')

    if image_src_parts[-1] == 'researchDollars.png':
        return 'RESEARCH_DOLLARS'
    elif image_src_parts[-1] == 'dollars.png':
        return 'DOLLARS'
    else:
        log(f"The bonus type could not be retrieved for image src '{bonus_image_src}'!", LogLevels.LOG_LEVEL_WARNING)
        return 'UNKNOWN'


def save_card_holder_results(parsed_results: Dict):
    """
    Saves the free Card Holder results to a json file
    :param parsed_results:
    :return:
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'card_holder_results__{timestamp}.json'
    filepath = os.path.join(os.getenv('CARD_HOLD_RESULTS_FOLDER', '/data/card_hold_results'), filename)

    save_dict_to_json(parsed_results, filepath)
