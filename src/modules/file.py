import csv
import json
import os

from typing import Dict

class FileMode:
    """
    Enum class to store the possible file opening modes
    """
    FILE_MODE_READ = 'r'
    FILE_MODE_WRITE = 'w'
    FILE_MODE_APPEND = 'a'
    FILE_MODE_BINARY = 'b'
    FILE_MODE_EXCLUSIVE = 'x'
    FILE_MODE_TEXT = 't'
    FILE_MODE_UPDATING = '+'


def save_dict_to_csv(input_dict, output_filepath, file_mode: str = FileMode.FILE_MODE_WRITE):
    """
    Saves a dictionary to a CSV file, using the keys of the first element in the dict to determine the CSV headers.
    :param input_dict:
    :param output_filepath:
    :param file_mode:
    :return:
    """
    folder = os.path.dirname(output_filepath)
    os.makedirs(folder, exist_ok=True)

    with open(output_filepath, file_mode, newline='') as output_csv:
        csv_writer = csv.writer(output_csv, dialect='excel')

        # Headers
        csv_writer.writerow(input_dict[0].keys())

        # Data
        for row in input_dict:
            csv_writer.writerow(row.values())


def save_dict_to_json(input_dict: Dict, output_filepath: str, file_mode: str = FileMode.FILE_MODE_WRITE):
    """
    Saves a dictionary to a JSON file
    :param input_dict:
    :param output_filepath:
    :param file_mode:
    :return:
    """
    folder = os.path.dirname(output_filepath)
    os.makedirs(folder, exist_ok=True)

    with open(output_filepath, file_mode) as f:
        json.dump(input_dict, f, ensure_ascii=False, indent=4)


def save_text_to_file(input_text: str, output_filepath: str, file_mode: str = FileMode.FILE_MODE_WRITE):
    """
    Saves a raw text input to a file
    :param input_text:
    :param output_filepath:
    :param file_mode:
    :return:
    """
    folder = os.path.dirname(output_filepath)
    os.makedirs(folder, exist_ok=True)

    with open(output_filepath, file_mode) as f:
        f.write(input_text)
