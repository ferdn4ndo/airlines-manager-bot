import os
import requests

from bs4 import BeautifulSoup
from bs4.element import ResultSet
from requests.cookies import RequestsCookieJar
from typing import Tuple, Dict, List

from .common import check_has_next_page, sanitize_text, save_dict_to_csv
from .user_agent import get_base_headers


def fetch_all_airplanes(cookies: RequestsCookieJar) -> List:
    """
    Retrieves a list with all the airplanes registered in the account (and their summarized data), saving the output
    to a CSV file.
    :param cookies:
    :return:
    """
    has_next = True
    page = 1
    airplanes = []

    while has_next:
        page_airplanes, has_next = get_page_airplanes(cookies, page)
        airplanes.extend(page_airplanes)
        page += 1

    save_dict_to_csv(airplanes, os.environ['AIRPLANES_SUMMARY_FILEPATH'])
    print(
        "Finished fetching {} airplanes! (summary exported to {})".format(
            len(airplanes),
            os.environ['AIRPLANES_SUMMARY_FILEPATH']
        )
    )

    return airplanes


def get_page_airplanes(cookies: RequestsCookieJar, page: int = 1) -> Tuple:
    """
    Retrieves a tuple of 2 items, containing the List of the airplanes in that page and if there's a next page
    available.
    :param cookies:
    :param page:
    :return:
    """
    airplanes = requests.get(
        'https://tycoon.airlines-manager.com/aircraft?page=' + str(page),
        headers=get_base_headers(),
        cookies=cookies,
    )
    airplanes_bs = BeautifulSoup(airplanes.text, 'html.parser')

    airplanes_table = airplanes_bs.find('table', attrs={'class': 'aircraftListViewTable'})
    airplanes_rows = airplanes_table.find_all('tr')
    print("Found a total of {} rows in page {}.".format(len(airplanes_rows), page))
    airplanes = [parse_airplane_row(row) for row in airplanes_rows]
    airplanes = [airplane for airplane in airplanes if not len(airplane) == 0]

    return airplanes, check_has_next_page(airplanes_bs)


def parse_airplane_row(row: ResultSet) -> Dict:
    """
    Parses a BS4 table row from the airplanes results page into a dict represent one single airplane.
    :param row:
    :return:
    """
    if len(row.find_all('th')) > 0:
        return {}

    aicraft_name_cell = row.find('span', attrs={'class': 'editAircraftName'})
    cells = row.find_all('td')

    return {
        'id': int(str(aicraft_name_cell['data-url']).split('/')[-1]),
        'name': aicraft_name_cell.text,
        'model': sanitize_text(str(cells[0].text).split('/')[0]),
        'model_img_url': cells[0].find('img', attrs={'class': 'zoomAircraft'})['data-aircraftimg'],
        'url': str(aicraft_name_cell['data-url']),
        'hub': sanitize_text(cells[1].text[:3]),
        'hub_flag_alt': cells[1].find('img')['alt'],
        'hub_flag_url': cells[1].find('img')['src'],
        'range': sanitize_text(cells[2].text),
        'usage': sanitize_text(cells[3].text),
        'wearing': sanitize_text(cells[4].text),
        'age': sanitize_text(cells[5].text),
        'capacity': sanitize_text(cells[6].text),
        'result_last_7_days': sanitize_text(cells[7].text),
    }
