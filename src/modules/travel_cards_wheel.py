import json
import os
from datetime import datetime
from typing import Dict

from bs4 import BeautifulSoup

from modules.file import save_dict_to_json, save_error_dump_file
from modules.logger import log, LogLevels
from modules.session_manager import SessionManager


def spin_travel_cards_wheel_if_available(session_manager: SessionManager):
    """
    Checks if the Travel Cards wheel is available, and spin it if so
    :param session_manager:
    :return:
    """
    if not is_travel_cards_wheel_available(session_manager=session_manager):
        return

    spin_result = spin_travel_cards_wheel(session_manager=session_manager)
    log("Travel Card Wheel spin Results: {}".format(json.dumps(spin_result)))


def is_travel_cards_wheel_available(session_manager: SessionManager) -> bool:
    """
    Determines if the Travel Cards Wheel is available to spin
    :param session_manager:
    :return:
    """
    home_response = session_manager.request(
        url='http://tycoon.airlines-manager.com/home',
        method=SessionManager.Methods.GET,
    )
    home_bs = BeautifulSoup(home_response.text, 'html.parser')

    main_content_div = home_bs.find('div', attrs={'id': 'mainContent'})
    if main_content_div is None:
        log("Aborting workshop reading as the items rack div was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=home_response.text, tag='home_main_content_div_not_found')
        raise ReferenceError("The home content div was not found")

    has_play_wheel_banner = home_bs.find('div', attrs={'id': 'playWheel'}) is not None
    log("Travel Cards Wheel available: {}".format('YES' if has_play_wheel_banner else 'NO'))

    return has_play_wheel_banner


def spin_travel_cards_wheel(session_manager: SessionManager) -> Dict:
    """
    Spin the Travel Cards Wheel, save and return the results (must check if available first!)
    :param session_manager:
    :return:
    """
    wheel_spin_result = session_manager.request(
        url='http://tycoon.airlines-manager.com/home/wheeltcgame/play',
        method=SessionManager.Methods.GET,
        extra_headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'http://tycoon.airlines-manager.com/home/wheeltcgame',
            'X-Requested-With': 'XMLHttpRequest',
        },
    )

    original_json_data = json.loads(wheel_spin_result.text)

    parsed_results = {
        'totalTravelCardsAfter': int(original_json_data['nbOfTravelCards']),
        'totalTravelCardsBefore': int(original_json_data['nbOfTravelCards']) - int(original_json_data['gain']),
        'earnedTravelCards': int(original_json_data['gain']),
        'bonusMultiplierGain': float(original_json_data['multiplierBonus']),
        'bonusMultiplierGainIndex': int(original_json_data['indexScore']),
        'canPlayAgain': bool(original_json_data['isAllowToPlay']),
    }

    save_travel_cards_results(parsed_results)

    return parsed_results


def save_travel_cards_results(parsed_results: Dict):
    """
    Saves the Travel Cards Wheel spin results to a json file
    :param parsed_results:
    :return:
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = 'travel_cards_wheel_results__{}.json'.format(timestamp)
    filepath = os.path.join(os.environ['TRAVEL_CARDS_RESULTS_FOLDER'], filename)

    save_dict_to_json(parsed_results, filepath)
