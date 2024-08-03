from bs4 import BeautifulSoup

from api.models import Line
from api.services import logging
from api.services.am_session import AmSessionManager
from api.services.error import ErrorDumpService


class LinesAuditionService:
    def __init__(self, session_manager: AmSessionManager, line_model: Line):
        self.logger = logging.get_logger(__name__)
        self.session_manager = session_manager
        self.line_model = line_model

    def execute_line_audition(self):
        """
        Update the ideal cost of the line, running an audition on the line
        :return:
        """
        self.logger.debug("Entering execute_line_audition method")
        update_audit_response = self.session_manager.request(
            url=f'http://tycoon.airlines-manager.com/marketing/internalaudit/line/{self.line_model.am_id}?fromPricing=1',
            method=AmSessionManager.Methods.GET,
            allow_redirects=False,
            extra_headers={
                'Referer': f'http://tycoon.airlines-manager.com/marketing/pricing/{self.line_model.am_id}/',
            },
        )

        if update_audit_response.status_code != 302:
            self.logger.error(f"Aborting line {self.line_model.name} price audit as the response code was not 302!")
            ErrorDumpService().save_error_dump_file(dump=update_audit_response.text, tag='lines_audit_response_not_302')

            raise ReferenceError(f"Received status code {update_audit_response.status_code} when expecting 302!")

        self.logger.error(
            "Audit data updated for line {} for a cost of $ {}! ({} bytes received)".format(
                self.line_model.name,
                self.line_model.internal_audit_cost,
                len(update_audit_response.text),
            )
        )

    def update_line_costs_to_ideal(self):
        """
        Update the line costs, based on the 'line.ideal_cost' value
        :return:
        """
        self.logger.debug("Entering update_line_costs_to_ideal method")
        line_pricing_response = self.session_manager.request(
            url=f'http://tycoon.airlines-manager.com/marketing/pricing/{self.line_model.am_id}',
            method=AmSessionManager.Methods.GET,
            extra_headers={
                'Referer': f'http://tycoon.airlines-manager.com/network/showline/{self.line_model.am_id}/',
            },
        )
        line_pricing_bs = BeautifulSoup(line_pricing_response.text, 'html.parser')

        line_pricing_div = line_pricing_bs.find('div', attrs={'id': 'marketing_linePricing'})
        if line_pricing_div is None:
            self.logger.error(f"Aborting line {self.line_model.name} cost update as the line pricing div was not found!")
            ErrorDumpService().save_error_dump_file(dump=line_pricing_response.text, tag='lines_price_update_pricing_div_not_found')

            raise ReferenceError("Div with id marketing_linePricing was not found")

        line_token_input = line_pricing_div.find('input', attrs={'id': 'line__token'})
        if line_pricing_div is None:
            self.logger.error(f"Aborting line {self.line_model.name} cost update as the CSRF token input was not found!")
            ErrorDumpService().save_error_dump_file(dump=line_pricing_response.text, tag='lines_price_csrf_input_not_found')

            raise ReferenceError("Input with id line__token was not found")

        line_token = line_token_input['value']
        self.logger.info(f"Line price update CSRF token: {line_token}")

        price_update_payload = {
            'line[priceEco]': self.line_model.ideal_cost.economic,
            'line[priceBus]': self.line_model.ideal_cost.executive,
            'line[priceFirst]': self.line_model.ideal_cost.first_class,
            'line[priceCargo]': self.line_model.ideal_cost.cargo,
            'line[_token]': line_token,
        }
        line_pricing_update_response = self.session_manager.request(
            url=f'http://tycoon.airlines-manager.com/marketing/pricing/{self.line_model.am_id}',
            method=AmSessionManager.Methods.POST,
            payload=price_update_payload,
            extra_headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f'http://tycoon.airlines-manager.com/marketing/pricing/{self.line_model.am_id}/',
            },
        )
        self.logger.info(
           f"Line {self.line_model.name} had the prices updated! ({len(line_pricing_update_response.text)} bytes received)"
        )
