import datetime

from bs4 import BeautifulSoup

from models.airport import create_airport_from_dict
from models.demand import Demand
from models.line import Line
from models.price import Price
from modules.file import save_error_dump_file
from modules.lines_audit import update_line_audit_data, update_line_cost
from modules.lines_summary import fetch_lines_summary
from modules.logger import LogLevels, log
from modules.session_manager import SessionManager
from modules.strings import return_only_numbers, sanitize_text


def update_all_lines_data(session_manager: SessionManager):
    """
    Updates the data for all the account lines
    :param session_manager:
    :return:
    """
    lines = fetch_lines_summary(session_manager=session_manager)
    for line_dict in lines:
        line_id = int(line_dict['id'])
        line = Line(id=line_id)
        update_line_data(line=line, session_manager=session_manager)


def update_line_data(line: Line, session_manager: SessionManager):
    """
    Update all the data for a given line
    :param line:
    :param session_manager:
    :return:
    """
    log('Updating basic data for line ID {}'.format(line.id))
    update_basic_data(line=line, session_manager=session_manager)

    log('Updating marketing data for line ID {}'.format(line.id))
    update_marketing_data(line=line, session_manager=session_manager)

    if line.reliability_level > 50:
        log(f'Last audit for line ID {line.id} is not trustable ({line.reliability_level} > 50), refreshing...')
        update_line_audit_data(line=line, session_manager=session_manager)

    if line.can_update_prices and line.ideal_cost != line.current_cost:
        log(f'Line {line.name} has a price difference between ideal and actual and can be updated, updating...')
        update_line_cost(line=line, session_manager=session_manager)
        update_marketing_data(line=line, session_manager=session_manager)

    line.last_updated_at = datetime.datetime.now()
    line.persist_to_file()
    log(f'Finished fetching data for line {line.name} (ID: {line.id})!')


def update_basic_data(line: Line, session_manager: SessionManager):
    """
    Update the line basic data
    :param line:
    :param session_manager:
    :return:
    """
    line_details_response = session_manager.request(
        url=f'http://tycoon.airlines-manager.com/network/showline/{line.id}',
        method=SessionManager.Methods.GET,
        extra_headers={
            'Referer': 'http://tycoon.airlines-manager.com/network/',
        },
    )
    line_details_bs = BeautifulSoup(line_details_response.text, 'html.parser')

    content_div = line_details_bs.find('div', attrs={'id': 'content'})
    if content_div is None:
        log(
            "Aborting line basic data update on ID {} as the show line div was not found!".format(line.id),
            LogLevels.LOG_LEVEL_ERROR
        )
        save_error_dump_file(dump=line_details_response.text, tag='lines_basic_data_update_content_div_not_found')
        raise ReferenceError("Div with id showLine was not found")

    box1_li_items = content_div.find('ul', attrs={'id': 'box1'}).find_all('li')
    box2_li_items = content_div.find('ul', attrs={'id': 'box2'}).find_all('li')

    origin_text = sanitize_text(box1_li_items[3].find('b').text)
    destination_text = sanitize_text(box2_li_items[3].find('b').text)

    line.distance_km = return_only_numbers(box2_li_items[1].find('b').text)
    line.taxes = return_only_numbers(box2_li_items[2].find('b').text)

    line.origin = create_airport_from_dict({
        'abbrev': sanitize_text(origin_text.split('/')[0]),
        'name': sanitize_text(origin_text.split('/')[1]),
    })

    line.destination = create_airport_from_dict({
        'abbrev': sanitize_text(destination_text.split('/')[0]),
        'name': sanitize_text(destination_text.split('/')[1]),
    })

    line_title = content_div.find('div', attrs={'class': 'lineTitle'})
    line_title.find('span').decompose()
    line.display_name = sanitize_text(line_title.text)
    line.name = f'{line.origin.abbrev} / {line.destination.abbrev}'


def update_marketing_data(line: Line, session_manager: SessionManager):
    """
    Update the line marketing data
    :param line:
    :param session_manager:
    :return:
    """
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
        log(
            "Aborting line update on ID {} as the line pricing div was not found!".format(line.id),
            LogLevels.LOG_LEVEL_ERROR
        )
        save_error_dump_file(dump=line_pricing_response.text, tag='lines_ticket_update_pricing_div_not_found')
        raise ReferenceError("Div with id marketing_linePricing was not found")

    line_pricing_div_children = line_pricing_div.findChildren()
    line.total_demand = Demand(
        economic = return_only_numbers(line_pricing_div_children[17].text),
        executive = return_only_numbers(line_pricing_div_children[25].text),
        first_class = return_only_numbers(line_pricing_div_children[33].text),
        cargo = return_only_numbers(line_pricing_div_children[41].text),
    )
    line.ideal_cost = Price(
        economic = return_only_numbers(line_pricing_div_children[15].text),
        executive = return_only_numbers(line_pricing_div_children[23].text),
        first_class = return_only_numbers(line_pricing_div_children[31].text),
        cargo = return_only_numbers(line_pricing_div_children[39].text),
    )
    line.turnover = Price(
        economic = return_only_numbers(line_pricing_div_children[19].text),
        executive = return_only_numbers(line_pricing_div_children[27].text),
        first_class = return_only_numbers(line_pricing_div_children[35].text),
        cargo = return_only_numbers(line_pricing_div_children[43].text),
    )
    line.current_cost = Price(
        economic = return_only_numbers(line_pricing_div_children[62].text),
        executive = return_only_numbers(line_pricing_div_children[71].text),
        first_class = return_only_numbers(line_pricing_div_children[80].text),
        cargo = return_only_numbers(line_pricing_div_children[89].text),
    )
    internal_audit_cost_field = line_pricing_div.find('input', attrs={'id': 'internalAuditCost'})
    line.internal_audit_cost = int(internal_audit_cost_field['value'])
    line.last_audit_date = datetime.datetime.strptime(line_pricing_div_children[47].text, '%d/%m/%Y')
    line.reliability_level = return_only_numbers(str(line_pricing_div_children[54]['class']).split(' ')[1])
    line.can_update_prices = line_pricing_div.find('form') is not None