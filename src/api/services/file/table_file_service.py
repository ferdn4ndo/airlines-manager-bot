import csv
import json
import os

from api.services import logging

from .file_mode import FileMode


class TableFileService:
    def __init__(self, filepath: str):
        self.logger = logging.get_logger(__name__)
        self.filepath = filepath

    def save_list_to_csv(self, input_list: list, file_mode: str = FileMode.FILE_MODE_WRITE):
        """
        Saves a list of dictionaries to a CSV file, using the keys of the first row in the list to determine the CSV
        headers.
        :param input_list:
        :param file_mode:
        :return:
        """
        self.logger.debug("Entering save_dict_to_csv method")
        folder = os.path.dirname(self.filepath)
        os.makedirs(folder, exist_ok=True)

        with open(self.filepath, file_mode, newline='') as output_csv:
            csv_writer = csv.writer(output_csv, dialect='excel')

            # Headers
            csv_writer.writerow(input_list[0].keys())

            # Data
            for row in input_list:
                csv_writer.writerow(row.values())

    def save_list_to_json(self, input_list: list, file_mode: str = FileMode.FILE_MODE_WRITE):
        """
        Saves a list of dictionaries to a JSON file
        :param input_list:
        :param file_mode:
        :return:
        """
        self.logger.debug("Entering save_dict_to_json method")
        folder = os.path.dirname(self.filepath)
        os.makedirs(folder, exist_ok=True)

        with open(self.filepath, file_mode) as f:
            json.dump(input_list, f, ensure_ascii=False, indent=4)
