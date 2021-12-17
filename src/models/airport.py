import json
import os

from typing import Dict

from models.base_model import BaseModel
from modules.file import read_text_file, save_dict_to_json
from modules.logger import log, LogLevels


class Airport(BaseModel):
    """
    Model class representing the Airport resource
    """
    abbrev = None
    name = None

    serializable_fields = ['abbrev', 'name']

    def __init__(self, **kwargs):
        """
        Airport class constructor
        :param kwargs:
        """
        log("Instantiating Airport class", LogLevels.LOG_LEVEL_DEBUG)
        super(Airport, self).__init__(**kwargs)

        if 'id' in kwargs:
            self.load_from_file()

    def __str__(self):
        """
        Overrides the original string conversion method to add more information
        :return:
        """
        log("Entering Airport.__str__ method", LogLevels.LOG_LEVEL_DEBUG)

        return '{} - {}'.format(self.abbrev, self.name)

    def load_from_file(self):
        """
        Load the resource from a file stored locally
        :return:
        """
        log("Entering Airport.load_from_file method", LogLevels.LOG_LEVEL_DEBUG),

        if self.abbrev is None:
            raise ValueError("Cannot load airport from file without abbrev!")

        filepath = os.path.join(os.environ['AIRPORTS_OBJECTS_FOLDER'], f'{self.abbrev}.json')
        if not os.path.isfile(filepath):
            log(
                f"Skipping the load process of airport {self.abbrev} as the file {filepath} was not found.",
                level=LogLevels.LOG_LEVEL_WARNING,
            )
            return self

        line_json = json.loads(read_text_file(filepath=filepath))
        self.unserialize(line_json)

        return self

    def persist_to_file(self):
        """
        Persist the resource to a file stored locally
        :return:
        """
        log("Entering Airport.persist_to_file method", LogLevels.LOG_LEVEL_DEBUG)

        if self.abbrev is None:
            raise ValueError("Cannot persist airport to file without abbrev!")

        filepath = os.path.join(os.environ['AIRPORTS_OBJECTS_FOLDER'], f'{self.abbrev}.json')
        save_dict_to_json(input_dict=self.serialize(), output_filepath=filepath)
        log(f"Persisted airport {self.abbrev} to file {filepath}!", LogLevels.LOG_LEVEL_DEBUG)


def create_airport_from_dict(data_dict: Dict) -> Airport:
    """
    Factory method to create a Airport model from a given dict
    :param data_dict:
    :return:
    """
    log("Entering create_airport_from_dict method", LogLevels.LOG_LEVEL_DEBUG)

    airport = Airport()
    airport.unserialize(data_dict)

    return airport
