import os

from bs4 import BeautifulSoup

from api.services import logging
from api.services.am_session import AmSessionManager
from api.services.error import ErrorDumpService
from api.services.file import TableFileService
from api.services.line import LineService
from api.services.strings import StringsService


class LinesSummaryService:

    def __init__(self, session_manager: AmSessionManager):
        self.logger = logging.get_logger(__name__)
        self.strings_service = StringsService()
        self.session_manager = session_manager

    def fetch_lines_list_from_summary(self, only_first_page: bool = False) -> list:
        self.logger.debug("Entering fetch_lines_list_from_summary method")
        summary = self.fetch_lines_summary(only_first_page=only_first_page)

        return [
            LineService().get_or_create_line_by_am_id(am_id=line_dict['id'])
            for line_dict in summary
        ]

    def fetch_lines_summary(self, only_first_page: bool = False) -> list:
        """
        Fetches the summary of all lines for the user account
        :return:
        """
        self.logger.debug("Entering fetch_lines_summary method")
        has_next = True
        page = 1
        lines_summary = []

        while has_next:
            page_lines, has_next = self.fetch_lines_summary_from_page(page)
            lines_summary.extend(page_lines)
            self.logger.info(
                f"Finished fetching summary page {page} with {len(page_lines)} results (has_next: {has_next})"
            )
            page += 1

            if only_first_page and has_next:
                self.logger.info("Skipping summary page loading after first page as required!")
                has_next = False

        lines_summary_filepath = os.getenv('LINES_SUMMARY_FILEPATH', '/data/lines_summary.csv')

        table_file_service = TableFileService(filepath=lines_summary_filepath)
        table_file_service.save_list_to_csv(input_list=lines_summary)

        self.logger.info(f"Finished listing {len(lines_summary)} lines! (summary exported to {lines_summary_filepath})")

        return lines_summary

    def fetch_lines_summary_from_page(self, page: int = 1) -> tuple:
        """
        Retrieves a tuple of 2 items, containing the List of the lines in that page and if there's a next page available.
        :param page:
        :return:
        """
        self.logger.debug("Entering fetch_lines_summary_from_page method")
        lines = self.session_manager.request(
            url='http://tycoon.airlines-manager.com/network/?page=' + str(page),
            method=AmSessionManager.Methods.GET,
        )
        lines_bs = BeautifulSoup(lines.text, 'html.parser')

        amgold_lines_table = lines_bs.find('div', attrs={'id': 'displayPro'})
        if amgold_lines_table is None:
            self.logger.error("Aborting lines reading as the AM Gold lines table was not found!")

            ErrorDumpService().save_error_dump_file(dump=lines.text, tag='lines_amgold_table_not_found')

            raise ReferenceError("Div with id displayPro was not found")

        lines_table = amgold_lines_table.find_all('table')[1]
        lines_rows = lines_table.find_all('tr')
        self.logger.info("Found a total of {} rows in page {}.".format(len(lines_rows), page))
        lines = [self.parse_line_summary_row(row) for row in lines_rows]
        lines = [line for line in lines if len(line) > 0]

        return lines, self.check_has_next_page(lines_bs)

    def parse_line_summary_row(self, row: BeautifulSoup) -> dict:
        """
        Parses a BS4 table row from the lines results page into a dict represent one single line.
        :param row:
        :return:
        """
        self.logger.debug("Entering parse_line_summary_row method")
        if len(row.find_all('th')) > 0:
            return {}

        cells = row.find_all('td')

        return {
            'id': int(str(cells[6].find('a')['href']).split('/')[-1]),
            'name': self.strings_service.sanitize_text(cells[0].text),
            'origin': self.strings_service.sanitize_text(str(cells[0].text).split('/')[0]),
            'destination': self.strings_service.sanitize_text(str(cells[0].text).split('/')[1]),
            'country_flag_alt': cells[0].find('img')['alt'],
            'country_flag_url': cells[0].find('img')['src'],
            'distance': self.strings_service.sanitize_text(cells[1].text),
            'remaining_demand': self.strings_service.sanitize_text(cells[2].text),
            'turnover': self.strings_service.sanitize_text(cells[3].text),
            'result_last_1_day': self.strings_service.sanitize_text(cells[4].text),
            'result_last_7_days': '--ToDo--',
            'url': cells[6].find('a')['href'],
        }

    def check_has_next_page(self, html_bs: BeautifulSoup) -> bool:
        """
        Determines if there's a next page available in a BS4 HTML results page.
        :param html_bs:
        :return:
        """
        self.logger.debug("Entering check_has_next_page method")

        next_div = html_bs.find('div', attrs={'class': 'pagination'}).find_all('span', attrs={'class': 'next'})

        return len(next_div) > 0
