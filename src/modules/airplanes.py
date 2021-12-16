import os

from bs4 import BeautifulSoup
from bs4.element import ResultSet
from typing import Tuple, Dict, List

from modules.file import save_dict_to_csv, save_error_dump_file
from modules.logger import log, LogLevels
from modules.pagination import check_has_next_page
from modules.session_manager import SessionManager
from modules.strings import sanitize_text


def fetch_all_airplanes(session_manager: SessionManager) -> List:
    """
    Retrieves a list with all the airplanes registered in the account (and their summarized data), saving the output
    to a CSV file.
    :param session_manager:
    :return:
    """
    has_next = True
    page = 1
    airplanes = []

    while has_next:
        page_airplanes, has_next = get_page_airplanes(session_manager=session_manager, page=page)
        airplanes.extend(page_airplanes)
        page += 1

    airplanes_summary_filepath = os.getenv('AIRPLANES_SUMMARY_FILEPATH', '/data/airplanes_summary.csv')
    save_dict_to_csv(airplanes, airplanes_summary_filepath)
    log(f"Finished fetching {len(airplanes)} airplanes! (summary exported to {airplanes_summary_filepath})")

    return airplanes


def get_page_airplanes(session_manager: SessionManager, page: int = 1) -> Tuple:
    """
    Retrieves a tuple of 2 items, containing the List of the airplanes in that page and if there's a next page
    available.
    :param session_manager:
    :param page:
    :return:
    """
    referer_endpoint = 'home/' if page <= 1 else f'aircraft?page={page - 1}'
    airplanes = session_manager.request(
        url='http://tycoon.airlines-manager.com/aircraft?page=' + str(page),
        method=SessionManager.Methods.GET,
        extra_headers={
            'Referer': f'http://tycoon.airlines-manager.com/{referer_endpoint}',
        },
    )
    airplanes_bs = BeautifulSoup(airplanes.text, 'html.parser')

    airplanes_table = airplanes_bs.find('table', attrs={'class': 'aircraftListViewTable'})
    if airplanes_table is None:
        log("Aborting airplanes reading as the airplanes table was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=airplanes.text, tag='airplanes_table_not_found')
        raise ReferenceError("Table with class aircraftListViewTable was not found")

    airplanes_rows = airplanes_table.find_all('tr')
    log("Found a total of {} rows in page {}.".format(len(airplanes_rows), page))
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

    airplane_name_cell = row.find('span', attrs={'class': 'editAircraftName'})
    cells = row.find_all('td')

    return {
        'id': int(str(airplane_name_cell['data-url']).split('/')[-1]),
        'name': airplane_name_cell.text,
        'model': sanitize_text(str(cells[0].text).split('/')[0]),
        'model_img_url': cells[0].find('img', attrs={'class': 'zoomAircraft'})['data-aircraftimg'],
        'url': str(airplane_name_cell['data-url']),
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
