import requests

from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar
from typing import List

from .user_agent import get_base_headers


def get_free_workshop_items(cookies: RequestsCookieJar):
    """
    Checks if there are free workshop items to be purchased, and gets them if so
    :param cookies:
    :return:
    """
    workshop_items = retrieve_all_workshop_items(cookies)
    free_items = filter_free_workshop_items(workshop_items)
    print("Total Workshop free items: {}".format(len(free_items)))

    for item in free_items:
        retrieve_workshop_item(cookies, item)


def retrieve_all_workshop_items(cookies: RequestsCookieJar) -> List:
    """
    Retrieves all the workshop items
    :param cookies:
    :return:
    """
    card_holder_response = requests.get(
        'https://tycoon.airlines-manager.com/shop/workshop',
        headers=get_base_headers({
            'Referer': 'https://tycoon.airlines-manager.com/home',
        }),
        cookies=cookies,
    )
    card_holder_bs = BeautifulSoup(card_holder_response.text, 'html.parser')
    items_rack = card_holder_bs.find('div', attrs={'class': 'rack'})

    if items_rack is None:
        return []

    return list(items_rack.find_all('div', attrs={'class': 'object'}))


def filter_free_workshop_items(workshop_items: List) -> List:
    """
    Filter a list with all the workshop items, leaving only the free ones
    :param workshop_items:
    :return:
    """
    return [
        item for item in workshop_items
        if 'Gratuito' in item.text
    ]


def retrieve_workshop_item(cookies: RequestsCookieJar, item: BeautifulSoup) -> bool:
    """
    Purchase the free workshop item, save and return the results (must check if available first!)
    :param item:
    :param cookies:
    :return:
    """
    item_url = item.find('a')['href']
    print('Getting free workshop item: ' + item_url)

    free_card_holder_response = requests.post(
        'https://tycoon.airlines-manager.com' + item_url,
        headers=get_base_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': 'https://tycoon.airlines-manager.com/shop/workshop',
            'Accept-Language': 'en-US,en;q=0.9',
        }),
        cookies=cookies,
        allow_redirects=False,
    )

    item_retrieved_successfully = free_card_holder_response.status_code == 302
    print("Retrieved item {} with {}".format(item_url, "SUCCESS" if item_retrieved_successfully is True else "FAILURE"))

    # To resume the flow
    retrieve_all_workshop_items(cookies)

    return item_retrieved_successfully
