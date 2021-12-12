import os
import requests

from bs4 import BeautifulSoup
from bs4.element import ResultSet
from requests.cookies import RequestsCookieJar
from typing import Tuple, Dict, List

from .file import save_dict_to_csv
from .logger import save_error_dump, log
from .pagination import check_has_next_page
from .strings import sanitize_text
from .user_agent import get_base_headers


def fetch_all_lines(cookies: RequestsCookieJar) -> List:
    """
    Retrieves a list with all the airplanes registered in the account (and their summarized data), saving the output
    to a CSV file.
    :param cookies:
    :return:
    """
    has_next = True
    page = 1
    lines = []

    while has_next:
        page_lines, has_next = get_page_lines(cookies, page)
        lines.extend(page_lines)
        page += 1

    save_dict_to_csv(lines, os.environ['LINES_SUMMARY_FILEPATH'])
    log(
        "Finished fetching {} lines! (summary exported to {})".format(
            len(lines),
            os.environ['LINES_SUMMARY_FILEPATH']
        )
    )

    return lines


def get_page_lines(cookies: RequestsCookieJar, page: int = 1) -> Tuple:
    """
    Retrieves a tuple of 2 items, containing the List of the lines in that page and if there's a next page available.
    :param cookies:
    :param page:
    :return:
    """
    lines = requests.get(
        'https://tycoon.airlines-manager.com/network/?page=' + str(page),
        headers=get_base_headers(),
        cookies=cookies,
    )
    lines_bs = BeautifulSoup(lines.text, 'html.parser')

    amgold_lines_table = lines_bs.find('div', attrs={'id': 'displayPro'})
    if amgold_lines_table is None:
        log("Aborting lines reading as the AM Gold lines table was not found!", )
        save_error_dump(dump=lines.text, tag='lines_amgold_table_not_found')
        raise ReferenceError("Div with id displayPro was not found")

    lines_table = amgold_lines_table.find_all('table')[1]
    lines_rows = lines_table.find_all('tr')
    log("Found a total of {} rows in page {}.".format(len(lines_rows), page))
    lines = [parse_line_row(row) for row in lines_rows]
    lines = [line for line in lines if not len(line) == 0]

    return lines, check_has_next_page(lines_bs)


def parse_line_row(row: ResultSet) -> Dict:
    """
    Parses a BS4 table row from the lines results page into a dict represent one single line.
    :param row:
    :return:
    """
    if len(row.find_all('th')) > 0:
        return {}

    cells = row.find_all('td')

    return {
        'id': int(str(cells[6].find('a')['href']).split('/')[-1]),
        'name': sanitize_text(cells[0].text),
        'origin': sanitize_text(str(cells[0].text).split('/')[0]),
        'destination': sanitize_text(str(cells[0].text).split('/')[1]),
        'country_flag_alt': cells[0].find('img')['alt'],
        'country_flag_url': cells[0].find('img')['src'],
        'distance': sanitize_text(cells[1].text),
        'remaining_demand': sanitize_text(cells[2].text),
        'turnover': sanitize_text(cells[3].text),
        'result_last_1_day': sanitize_text(cells[4].text),
        'result_last_7_days': '--ToDo--',
        'url': cells[6].find('a')['href'],
    }
