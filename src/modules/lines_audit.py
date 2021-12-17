from bs4 import BeautifulSoup

from models.line import Line
from modules.file import save_error_dump_file
from modules.logger import log, LogLevels
from modules.session_manager import SessionManager


def update_line_audit_data(line: Line, session_manager: SessionManager):
    """
    Update the ideal cost of the line, running an audition on the line
    :param line:
    :param session_manager:
    :return:
    """
    log("Entering update_line_audit_data method", LogLevels.LOG_LEVEL_DEBUG)
    update_audit_response = session_manager.request(
        url=f'http://tycoon.airlines-manager.com/marketing/internalaudit/line/{line.id}?fromPricing=1',
        method=SessionManager.Methods.GET,
        allow_redirects=False,
        extra_headers={
            'Referer': f'http://tycoon.airlines-manager.com/marketing/pricing/{line.id}/',
        },
    )

    if not update_audit_response.status_code == 302:
        log(f"Aborting line {line.name} price audit as the response code was not 302!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=update_audit_response.text, tag='lines_audit_response_not_302')
        raise ReferenceError(f"Received status code {update_audit_response.status_code} when expecting 302!")

    log(
        "Audit data updated for line {} for a cost of $ {}! ({} bytes received)".format(
            line.name,
            line.internal_audit_cost,
            len(update_audit_response.text),
        )
    )


def update_line_cost(line: Line, session_manager: SessionManager):
    """
    Update the line costs, based on the 'line.ideal_cost' value
    :param line:
    :param session_manager:
    :return:
    """
    log("Entering update_line_cost method", LogLevels.LOG_LEVEL_DEBUG)
    line_pricing_response = session_manager.request(
        url=f'http://tycoon.airlines-manager.com/marketing/pricing/{line.id}',
        method=SessionManager.Methods.GET,
        extra_headers={
            'Referer': f'http://tycoon.airlines-manager.com/network/showline/{line.id}/',
        },
    )
    line_pricing_bs = BeautifulSoup(line_pricing_response.text, 'html.parser')

    line_pricing_div = line_pricing_bs.find('div', attrs={'id': 'marketing_linePricing'})
    if line_pricing_div is None:
        log(f"Aborting line {line.name} cost update as the line pricing div was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=line_pricing_response.text, tag='lines_price_update_pricing_div_not_found')
        raise ReferenceError("Div with id marketing_linePricing was not found")

    line_token_input = line_pricing_div.find('input', attrs={'id': 'line__token'})
    if line_pricing_div is None:
        log(f"Aborting line {line.name} cost update as the CSRF token input was not found!", LogLevels.LOG_LEVEL_ERROR)
        save_error_dump_file(dump=line_pricing_response.text, tag='lines_price_csrf_input_not_found')
        raise ReferenceError("Input with id line__token was not found")

    line_token = line_token_input['value']
    log(f"Line price update CSRF token: {line_token}", LogLevels.LOG_LEVEL_NOTICE)

    price_update_payload = {
        'line[priceEco]': line.ideal_cost.economic,
        'line[priceBus]': line.ideal_cost.executive,
        'line[priceFirst]': line.ideal_cost.first_class,
        'line[priceCargo]': line.ideal_cost.cargo,
        'line[_token]': line_token,
    }
    line_pricing_update_response = session_manager.request(
        url=f'http://tycoon.airlines-manager.com/marketing/pricing/{line.id}',
        method=SessionManager.Methods.POST,
        payload=price_update_payload,
        extra_headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'http://tycoon.airlines-manager.com/marketing/pricing/{line.id}/',
        },
    )
    log(
        f"Line {line.name} had the prices updated! ({len(line_pricing_update_response.text)} bytes received)",
        LogLevels.LOG_LEVEL_NOTICE
    )
