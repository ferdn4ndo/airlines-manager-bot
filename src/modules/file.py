import csv
import json
import os
import pickle

from datetime import datetime
from requests.cookies import RequestsCookieJar
from typing import Dict

from modules.logger import log, LogLevels


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
    log("Entering save_dict_to_csv method", LogLevels.LOG_LEVEL_DEBUG)
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
    log("Entering save_dict_to_json method", LogLevels.LOG_LEVEL_DEBUG)
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
    log("Entering save_text_to_file method", LogLevels.LOG_LEVEL_DEBUG)
    folder = os.path.dirname(output_filepath)
    os.makedirs(folder, exist_ok=True)

    with open(output_filepath, file_mode) as f:
        f.write(input_text)


def check_if_file_exists(filepath: str):
    """
    Check if a given filepath exists and raise a FileNotFoundError if not
    :param filepath:
    :return:
    """
    log("Entering check_if_file_exists method", LogLevels.LOG_LEVEL_DEBUG)
    if not os.path.isfile(filepath):
        log(f"Unable to locate file {filepath}!", LogLevels.LOG_LEVEL_ERROR)
        raise FileNotFoundError(f"Unable to locate file {filepath}!")


def read_text_file(filepath: str, file_mode: str = FileMode.FILE_MODE_READ):
    """
    Reads a file to a string
    :param filepath:
    :param file_mode:
    :return:
    """
    log("Entering read_text_file method", LogLevels.LOG_LEVEL_DEBUG)
    check_if_file_exists(filepath)

    with open(filepath, file_mode) as f:
        data = f.read()

    return data


def read_binary_file(filepath: str, file_mode: str = FileMode.FILE_MODE_READ + FileMode.FILE_MODE_BINARY):
    """
    Reads a file to a string
    :param filepath:
    :param file_mode:
    :return:
    """
    log("Entering read_binary_file method", LogLevels.LOG_LEVEL_DEBUG)
    check_if_file_exists(filepath)

    with open(filepath, file_mode) as f:
        data = pickle.load(f)

    return data


def read_cookies_file() -> RequestsCookieJar:
    """
    Reads the cookies data file into a RequestsCookieJar object to be used with authorized requests.
    :return:
    """
    log("Entering read_cookies_file method", LogLevels.LOG_LEVEL_DEBUG)
    return read_binary_file(filepath=os.getenv('COOKIES_FILEPATH', '/data/cookies.dat'))


def save_cookies_file(cookies: RequestsCookieJar):
    """
    Saves the cookies data (from a RequestsCookieJar object) to the file.
    :param cookies:
    :return:
    """
    log("Entering save_cookies_file method", LogLevels.LOG_LEVEL_DEBUG)
    cookies_filepath = os.getenv('COOKIES_FILEPATH', '/data/cookies.dat')
    with open(cookies_filepath, 'wb') as cookies_file:
        pickle.dump(cookies, cookies_file)


def save_error_dump_file(dump: str, tag: str = 'dump'):
    """
    Saves an error dump to a file
    :param dump:
    :param tag:
    :return:
    """
    log("Entering save_error_dump_file method", LogLevels.LOG_LEVEL_DEBUG)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = '{}_{}.txt'.format(timestamp, tag)
    filepath = os.path.join(os.getenv('ERROR_DUMPS_FOLDER', '/data/error_dumps'), filename)
    save_text_to_file(dump, filepath)
    log("Saved error dump to {}".format(filepath))
