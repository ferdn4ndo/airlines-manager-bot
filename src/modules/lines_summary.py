import os

from bs4 import BeautifulSoup
from bs4.element import ResultSet
from typing import List, Dict, Tuple

from modules.file import save_dict_to_csv, save_error_dump_file
from modules.logger import log
from modules.pagination import check_has_next_page
from modules.session_manager import SessionManager
from modules.strings import sanitize_text


def fetch_lines_summary(session_manager: SessionManager) -> List:
    """
    Fetches the summary of all lines for the user account
    :param session_manager:
    :return:
    """
    has_next = True
    page = 1
    lines_summary = []

    while has_next:
        page_lines, has_next = fetch_lines_summary_from_page(session_manager, page)
        lines_summary.extend(page_lines)
        page += 1

    lines_summary_filepath = os.getenv('LINES_SUMMARY_FILEPATH', '/data/lines_summary.csv')
    save_dict_to_csv(lines_summary, lines_summary_filepath)
    log(f"Finished indexing {len(lines_summary)} lines! (summary exported to {lines_summary_filepath})")

    return lines_summary


def fetch_lines_summary_from_page(session_manager: SessionManager, page: int = 1) -> Tuple:
    """
    Retrieves a tuple of 2 items, containing the List of the lines in that page and if there's a next page available.
    :param session_manager:
    :param page:
    :return:
    """
    lines = session_manager.request(
        url='http://tycoon.airlines-manager.com/network/?page=' + str(page),
        method=SessionManager.Methods.GET,
    )
    lines_bs = BeautifulSoup(lines.text, 'html.parser')

    amgold_lines_table = lines_bs.find('div', attrs={'id': 'displayPro'})
    if amgold_lines_table is None:
        log("Aborting lines reading as the AM Gold lines table was not found!", )
        save_error_dump_file(dump=lines.text, tag='lines_amgold_table_not_found')
        raise ReferenceError("Div with id displayPro was not found")

    lines_table = amgold_lines_table.find_all('table')[1]
    lines_rows = lines_table.find_all('tr')
    log("Found a total of {} rows in page {}.".format(len(lines_rows), page))
    lines = [parse_line_summary_row(row) for row in lines_rows]
    lines = [line for line in lines if not len(line) == 0]

    return lines, check_has_next_page(lines_bs)


def parse_line_summary_row(row: ResultSet) -> Dict:
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
