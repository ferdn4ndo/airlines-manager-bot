import csv
import json
import os.path
import re
from typing import Dict

from bs4 import BeautifulSoup


def check_has_next_page(html_bs: BeautifulSoup):
    """
    Determines if there's a next page available in a BS4 HTML results page.
    :param html_bs:
    :return:
    """
    next_div = html_bs.find('div', attrs={'class': 'pagination'}).find_all('span', attrs={'class': 'next'})
    return len(next_div) > 0


def sanitize_text(input_text) -> str:
    """
    Sanitizes a string parsed from HTML, removing extra spaces and newlines.
    :param input_text:
    :return:
    """
    return re.sub(r'\s+', ' ', str(input_text).strip())


def save_dict_to_csv(input_dict, output_filepath):
    """
    Saves a dictionary to a CSV file, using the keys of the first element in the dict to determine the CSV headers.
    :param input_dict:
    :param output_filepath:
    :return:
    """
    folder = os.path.dirname(output_filepath)
    os.makedirs(folder, exist_ok=True)

    with open(output_filepath, 'w', newline='') as output_csv:
        csv_writer = csv.writer(output_csv, dialect='excel')

        # Headers
        csv_writer.writerow(input_dict[0].keys())

        # Data
        for row in input_dict:
            csv_writer.writerow(row.values())


def save_dict_to_json(input_dict: Dict, output_filepath: str):
    """
    Saves a dictionary to a JSON file
    :param input_dict:
    :param output_filepath:
    :return:
    """
    folder = os.path.dirname(output_filepath)
    os.makedirs(folder, exist_ok=True)

    with open(output_filepath, 'w') as f:
        json.dump(input_dict, f, ensure_ascii=False, indent=4)
