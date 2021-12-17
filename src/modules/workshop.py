from bs4 import BeautifulSoup
from typing import List

from modules.file import save_error_dump_file
from modules.logger import log, LogLevels
from modules.session_manager import SessionManager
from modules.strings import return_only_numbers
from modules.user_agent import get_base_headers


def get_free_workshop_items(session_manager: SessionManager):
    """
    Checks if there are free workshop items to be purchased, and gets them if so
    :param session_manager:
    :return:
    """
    log("Entering get_free_workshop_items method", LogLevels.LOG_LEVEL_DEBUG)
    workshop_items = retrieve_all_workshop_items(session_manager=session_manager)
    free_items = filter_free_workshop_items(workshop_items)
    log(f"Total Workshop free items: {len(free_items)}")

    for item in free_items:
        retrieve_workshop_item(session_manager=session_manager, workshop_item=item)


def retrieve_all_workshop_items(session_manager: SessionManager) -> List:
    """
    Retrieves all the workshop items
    :param session_manager:
    :return:
    """
    log("Entering retrieve_all_workshop_items method", LogLevels.LOG_LEVEL_DEBUG)
    card_holder_response = session_manager.request(
        url='http://tycoon.airlines-manager.com/shop/workshop',
        method=SessionManager.Methods.GET,
        extra_headers=get_base_headers({
            'Referer': 'http://tycoon.airlines-manager.com/home',
        }),
    )
    card_holder_bs = BeautifulSoup(card_holder_response.text, 'html.parser')
    items_rack = card_holder_bs.find('div', attrs={'class': 'rack'})

    if items_rack is None:
        log("Aborting workshop reading as the items rack div was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=card_holder_response.text, tag='items_rack_div_not_found')
        raise ReferenceError("The workshop items div was not found")

    return list(items_rack.find_all('div', attrs={'class': 'object'}))


def filter_free_workshop_items(workshop_items: List) -> List:
    """
    Filter a list with all the workshop items, leaving only the free ones
    :param workshop_items:
    :return:
    """
    log("Entering filter_free_workshop_items method", LogLevels.LOG_LEVEL_DEBUG)

    return [
        item for item in workshop_items
        if is_free_item(item)
    ]


def is_free_item(workshop_item: BeautifulSoup) -> bool:
    """
    Determines if a given workshop item is free
    :param workshop_item:
    :return:
    """
    log("Entering is_free_item method", LogLevels.LOG_LEVEL_DEBUG)

    link = workshop_item.find('a', attrs={'class': 'purchaseButton useAjax'})
    if link is None:
        return False

    return return_only_numbers(link.text) is None


def retrieve_workshop_item(session_manager: SessionManager, workshop_item: BeautifulSoup) -> bool:
    """
    Purchase the free workshop item, save and return the results (must check if available first!)
    :param session_manager:
    :param workshop_item:
    :return:
    """
    log("Entering retrieve_workshop_item method", LogLevels.LOG_LEVEL_DEBUG)

    item_url = workshop_item.find('a')['href']
    log(f"Getting free workshop item: {item_url}")

    free_card_holder_response = session_manager.request(
        url='http://tycoon.airlines-manager.com' + item_url,
        method=SessionManager.Methods.POST,
        extra_headers={
            'Referer': 'http://tycoon.airlines-manager.com/shop/workshop',
        },
        allow_redirects=False,
    )

    item_retrieved_successfully = free_card_holder_response.status_code == 302
    log("Retrieved item {} with {}".format(item_url, 'SUCCESS' if item_retrieved_successfully is True else 'FAILURE'))

    # To resume the flow
    retrieve_all_workshop_items(session_manager=session_manager)

    return item_retrieved_successfully
