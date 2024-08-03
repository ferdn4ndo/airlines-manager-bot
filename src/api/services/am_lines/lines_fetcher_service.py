import json
import os
import re
import shutil
from datetime import datetime

from bs4 import BeautifulSoup

from api.models import Line, Airport
from api.services import logging
from api.services.airport import AirportService
from api.services.am_session import AmSessionManager
from api.services.error import ErrorDumpService
from api.services.strings import StringsService
from django.conf import settings

from .lines_summary_service import LinesSummaryService
from .lines_audition_service import LinesAuditionService


class LinesFetcherService:
    def __init__(self, session_manager: AmSessionManager, force_sync: bool = False, only_first_page: bool = False):
        self.logger = logging.get_logger(__name__)
        self.session_manager = session_manager
        self.strings_service = StringsService()
        self.force_sync = force_sync
        self.only_first_page = only_first_page

    def fetch_lines(self) -> list:
        self.logger.debug("Entering update_all_lines_data method")

        # Fetch the line list (and some basic data) from the summary pages
        lines_summary_service = LinesSummaryService(session_manager=self.session_manager)
        lines = lines_summary_service.fetch_lines_list_from_summary(only_first_page=self.only_first_page)

        # Update the detailed data for each of the lines
        total_lines = len(lines)
        for index, line in enumerate(lines):
            percentage = "{0:.2f}%".format((index+1)*100/total_lines)
            self.logger.debug(f"Updating data for line {index+1} out of {total_lines} ({percentage})")
            self.update_line_data(line_model=line)

        return lines

    def is_line_data_old(self, line_model: Line) -> bool:
        if self.force_sync:
            self.logger.info(
                f"Line {line_model.name} (AM ID: {line_model.am_id}) will be updated the sync was forced"
            )

            return True

        if line_model.last_synced_at is None:
            self.logger.info(
                f"Line {line_model.name} (AM ID: {line_model.am_id}) will be updated no last sync date was found"
            )

            return True

        update_frequency_days = int(os.getenv('LINE_UPDATE_INTERVAL_DAYS', 2))
        delta_days = abs((datetime.now() - line_model.last_synced_at).days)
        if delta_days < update_frequency_days:
            self.logger.info(
                "No need to update line {} (AM ID: {}) as only {} day(s) have passed since last sync (expected {})".format(
                    line_model.name,
                    line_model.am_id,
                    delta_days,
                    update_frequency_days
                )
            )

            return False

        self.logger.info(
            "Line {} (AM ID: {}) will be updated as {} day(s) have passed since last sync (expected {})".format(
                line_model.name,
                line_model.am_id,
                delta_days,
                update_frequency_days
            )
        )

        return True

    def update_line_data(self, line_model: Line):
        """
        Update all the data for a given line
        :param line_model:
        :return:
        """
        self.logger.debug("Entering update_line_data method")

        if not self.is_line_data_old(line_model=line_model):
            return

        self.logger.info(f"Updating data for line AM ID {line_model.am_id}")

        self.logger.info(f"Updating basic data for line AM ID {line_model.am_id}")
        self.update_basic_data(line_model=line_model)

        self.logger.info(f"Updating marketing data for line AM ID {line_model.am_id}")
        self.update_marketing_data(line_model=line_model)

        audition_service = LinesAuditionService(session_manager=self.session_manager, line_model=line_model)

        if line_model.reliability_level > 50:
            self.logger.info(
                "Last audit for line {} (AM ID {}) is not trustable ({} > 50), refreshing...".format(
                    line_model.name,
                    line_model.am_id,
                    line_model.reliability_level
                )
            )
            audition_service.execute_line_audition()
            self.update_marketing_data(line_model=line_model)

        if line_model.can_update_prices and line_model.ideal_cost != line_model.current_cost:
            self.logger.info(f"Line {line_model.name} has a price difference between ideal and actual and can be updated, updating...")
            audition_service.update_line_costs_to_ideal()
            self.update_marketing_data(line_model=line_model)

        line_model.last_updated_at = datetime.now()
        line_model.save()

        self.logger.info(f"Finished fetching data for line {line_model.name} (ID: {line_model.id})!")

    def update_basic_data(self, line_model: Line):
        """
        Update the line basic data
        :param line_model:
        :return:
        """
        self.logger.debug("Entering update_basic_data method")
        line_details_response = self.session_manager.request(
            url=f'http://tycoon.airlines-manager.com/network/showline/{line_model.am_id}',
            method=AmSessionManager.Methods.GET,
            extra_headers={
                'Referer': 'http://tycoon.airlines-manager.com/network/',
            },
        )
        line_details_bs = BeautifulSoup(line_details_response.text, 'html.parser')

        content_div = line_details_bs.find('div', attrs={'id': 'content'})
        if content_div is None:
            self.logger.error(
                f"Aborting line basic data update on ID {line_model.am_id} as the show line div was not found!",
            )
            ErrorDumpService().save_error_dump_file(
                dump=line_details_response.text,
                tag='lines_basic_data_update_content_div_not_found'
            )

            raise ReferenceError("Div with id showLine was not found")

        box1_li_items = content_div.find('ul', attrs={'id': 'box1'}).find_all('li')
        box2_li_items = content_div.find('ul', attrs={'id': 'box2'}).find_all('li')

        line_title_div = content_div.find('div', attrs={'class': 'lineTitle'})
        line_title_div.find('span').decompose()

        origin_city = line_title_div.find('i').text
        line_title_div.find('i').decompose()
        self.logger.debug(f"Origin airport city: {origin_city}")

        destination_city = line_title_div.find('i').text
        line_title_div.find('i').decompose()
        self.logger.debug(f"Destination airport city: {destination_city}")

        line_title_text = self.strings_service.sanitize_text(line_title_div.text)
        self.logger.debug(f"Line title text: {line_title_text}")
        line_title_parts = re.split("/ [A-Z]{3} - ", line_title_text)
        line_title_parts[1] = line_title_text.replace(line_title_parts[0], '')[1:]
        self.logger.debug(f"Line title parts: {line_title_parts}")

        origin_text = str(line_title_parts[0]).strip().replace("- -", f"-")
        self.logger.debug(f"Origin airport text: {origin_text}")

        destination_text = str(line_title_parts[1]).strip().replace("- -", f"-")
        self.logger.debug(f"Destination airport text: {destination_text}")

        line_model.distance_km = self.strings_service.return_only_numbers(box2_li_items[1].find('b').text)
        line_model.taxes = self.strings_service.return_only_numbers(box2_li_items[2].find('b').text)
        line_model.total_airplanes_assigned = self.strings_service.return_only_numbers(box1_li_items[1].find('strong').text)
        line_model.total_weekly_flights = self.strings_service.return_only_numbers(box1_li_items[2].find('strong').text)

        map_data_text = content_div.find('div', attrs={'id': 'map_NetworkJson'}).text

        origin_line_div = box1_li_items[3].find('b')
        line_model.origin = self.parse_airport(
            airport_text=origin_text,
            airport_div_element=origin_line_div,
            city_name=origin_city,
            map_data_text=map_data_text,
        )

        destination_line_div = box2_li_items[3].find('b')
        line_model.destination = self.parse_airport(
            airport_text=destination_text,
            airport_div_element=destination_line_div,
            city_name=destination_city,
            map_data_text=map_data_text,
        )

        line_model.display_name = self.strings_service.sanitize_text(line_title_text).replace("- -", f"-")
        self.logger.debug(f"Parsed line display_name: {line_model.display_name}")

        line_model.name = f'{line_model.origin.iata_code} / {line_model.destination.iata_code}'
        self.logger.debug(f"Parsed Line name: {line_model.name}")

    def parse_airport(self, airport_text: str, city_name: str, airport_div_element: BeautifulSoup, map_data_text: str) -> Airport:
        airports_service = AirportService()

        iata_code=self.strings_service.sanitize_text(airport_text.split('-', 1)[0])

        map_data_json = json.loads(map_data_text)
        airport_data = [airport for airport in map_data_json['airports'] if airport['iata'] == iata_code][0]
        self.logger.debug(f"Parsed airport map data: {airport_data}")

        airport = airports_service.get_or_create_airport(
            iata_code=iata_code,
            name=self.strings_service.sanitize_text(airport_text.split('-', 1)[1]),
            city_name=city_name,
            country_name=self.strings_service.sanitize_text(airport_div_element.text.split('/', 1)[1]),
            country_flag_url=self.strings_service.sanitize_text(airport_div_element.find('img')['src']),
            latitude=airport_data['latitude'],
            longitude=airport_data['longitude'],
        )

        local_flag_path = f"{settings.BASE_DIR}/static{airport.country_flag_url}"
        self.logger.debug(f"Local flag path: {local_flag_path}")
        line_details_response = self.session_manager.request(
            url=f'http://tycoon.airlines-manager.com/{airport.country_flag_url}',
            method=AmSessionManager.Methods.GET,
            extra_headers={
                'Referer': 'http://tycoon.airlines-manager.com/network/',
            },
        )
        if not os.path.exists(local_flag_path):
            self.logger.debug(f"Downloading country flag to {local_flag_path}")
            with open(local_flag_path, 'wb') as file:
                file.write(line_details_response.content)
            self.logger.debug(f"Saved country flag to {local_flag_path}")

        self.logger.debug(f"Parsed airport code: {airport.iata_code}")
        self.logger.debug(f"Parsed airport name: {airport.name}")
        self.logger.debug(f"Parsed airport city name: {airport.city_name}")
        self.logger.debug(f"Parsed airport country name: {airport.country_name}")
        self.logger.debug(f"Parsed airport country flag url: {airport.country_flag_url}")
        self.logger.debug(f"Parsed airport latitude: {airport.latitude}")
        self.logger.debug(f"Parsed airport longitude: {airport.longitude}")

        return airport

    def update_marketing_data(self, line_model: Line):
        """
        Update the line marketing data
        :param line_model:
        :return:
        """
        self.logger.debug("Entering update_marketing_data method")
        line_pricing_response = self.session_manager.request(
            url=f'http://tycoon.airlines-manager.com/marketing/pricing/{line_model.am_id}',
            method=AmSessionManager.Methods.GET,
            extra_headers={
                'Referer': f'http://tycoon.airlines-manager.com/network/showline/{line_model.am_id}/',
            },
        )
        line_pricing_bs = BeautifulSoup(line_pricing_response.text, 'html.parser')

        line_pricing_div = line_pricing_bs.find('div', attrs={'id': 'marketing_linePricing'})
        if line_pricing_div is None:
            self.logger.error(f"Aborting line update on ID {line_model.id} as the line pricing div was not found!")
            ErrorDumpService().save_error_dump_file(
                dump=line_pricing_response.text,
                tag='lines_ticket_update_pricing_div_not_found'
            )
            raise ReferenceError("Div with id marketing_linePricing was not found")

        line_pricing_div_children = line_pricing_div.findChildren()
        line_model.update_total_demand(
            economic=self.strings_service.return_only_numbers(line_pricing_div_children[17].text),
            executive=self.strings_service.return_only_numbers(line_pricing_div_children[25].text),
            first_class=self.strings_service.return_only_numbers(line_pricing_div_children[33].text),
            cargo=self.strings_service.return_only_numbers(line_pricing_div_children[41].text),
        )
        line_model.update_ideal_cost(
            economic=float(self.strings_service.return_only_numbers(line_pricing_div_children[15].text)),
            executive=float(self.strings_service.return_only_numbers(line_pricing_div_children[23].text)),
            first_class=float(self.strings_service.return_only_numbers(line_pricing_div_children[31].text)),
            cargo=float(self.strings_service.return_only_numbers(line_pricing_div_children[39].text)),
        )
        line_model.update_turnover(
            economic=float(self.strings_service.return_only_numbers(line_pricing_div_children[19].text)),
            executive=float(self.strings_service.return_only_numbers(line_pricing_div_children[27].text)),
            first_class=float(self.strings_service.return_only_numbers(line_pricing_div_children[35].text)),
            cargo=float(self.strings_service.return_only_numbers(line_pricing_div_children[43].text)),
        )
        line_model.update_current_cost(
            economic=float(self.strings_service.return_only_numbers(line_pricing_div_children[62].text)),
            executive=float(self.strings_service.return_only_numbers(line_pricing_div_children[71].text)),
            first_class=float(self.strings_service.return_only_numbers(line_pricing_div_children[80].text)),
            cargo=float(self.strings_service.return_only_numbers(line_pricing_div_children[89].text)),
        )
        internal_audit_cost_field = line_pricing_div.find('input', attrs={'id': 'internalAuditCost'})
        line_model.internal_audit_cost = int(internal_audit_cost_field['value'])
        line_model.last_audit_date = datetime.strptime(line_pricing_div_children[47].text, '%d/%m/%Y')
        line_model.reliability_level = self.strings_service.return_only_numbers(
            str(line_pricing_div_children[54]['class']).split(' ')[1]
        )
        line_model.can_update_prices = line_pricing_div.find('form') is not None
