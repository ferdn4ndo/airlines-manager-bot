import datetime
import json
import os
from typing import Dict

from models.airport import create_airport_from_dict, Airport
from models.base_model import BaseModel
from models.demand import create_demand_from_dict, Demand
from models.price import create_price_from_dict, Price
from modules.file import read_text_file, save_dict_to_json
from modules.logger import log, LogLevels


class Line(BaseModel):
    """
    Model class representing the Line resource
    """
    id = None
    name = None
    display_name = None
    origin: Airport = None
    destination: Airport = None
    distance_km = None
    total_demand: Demand = None
    ideal_cost: Price = None
    turnover: Price = None
    current_cost: Price = None
    internal_audit_cost = None
    last_audit_date: datetime.datetime = None
    reliability_level: int = None
    taxes = None
    can_update_prices: bool = False
    last_updated_at: datetime.datetime = None

    serializable_fields = [
        'id',
        'name',
        'display_name',
        'origin',
        'destination',
        'distance_km',
        'total_demand',
        'ideal_cost',
        'turnover',
        'current_cost',
        'internal_audit_cost',
        'last_audit_date',
        'reliability_level',
        'taxes',
        'can_update_prices',
        'last_updated_at',
    ]

    def __init__(self, **kwargs):
        """
        Line class constructor
        :param kwargs:
        """
        super(Line, self).__init__(**kwargs)

        if 'id' in kwargs:
            self.load_from_file()

    def serialize(self) -> Dict:
        """
        Override the parent serialization method to resolve the nested objects
        :return:
        """
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'origin':  self.origin.serialize(),
            'destination': self.destination.serialize(),
            'distance_km': self.distance_km,
            'total_demand': self.total_demand.serialize(),
            'ideal_cost': self.ideal_cost.serialize(),
            'turnover': self.turnover.serialize(),
            'current_cost': self.current_cost.serialize(),
            'internal_audit_cost': self.internal_audit_cost,
            'last_audit_date': self.last_audit_date.isoformat(),
            'reliability_level': self.reliability_level,
            'taxes': self.taxes,
            'can_update_prices': self.can_update_prices,
            'last_updated_at': self.last_updated_at.isoformat(),
        }

    def unserialize(self, data_dict: Dict):
        """
        Override the parent de-serialization method to resolve the nested objects
        :param data_dict:
        :return:
        """
        special_fields = [
            'origin',
            'destination',
            'total_demand',
            'ideal_cost',
            'turnover',
            'current_cost',
            'last_audit_date',
            'last_updated_at',
        ]
        super().unserialize({field: data_dict[field] for field in data_dict.keys() if not field in special_fields})

        if 'origin' in data_dict:
            self.origin = create_airport_from_dict(data_dict['origin'])

        if 'destination' in data_dict:
            self.destination = create_airport_from_dict(data_dict['destination'])

        if 'total_demand' in data_dict:
            self.total_demand = create_demand_from_dict(data_dict['total_demand'])

        if 'ideal_cost' in data_dict:
            self.ideal_cost = create_price_from_dict(data_dict['ideal_cost'])

        if 'turnover' in data_dict:
            self.turnover = create_price_from_dict(data_dict['turnover'])

        if 'current_cost' in data_dict:
            self.current_cost = create_price_from_dict(data_dict['current_cost'])

        if 'last_audit_date' in data_dict:
            self.last_audit_date = datetime.datetime.fromisoformat(data_dict['last_audit_date'])

        if 'last_updated_at' in data_dict:
            self.last_updated_at = datetime.datetime.fromisoformat(data_dict['last_updated_at'])

        return self

    def load_from_file(self):
        """
        Load the resource from a file stored locally
        :return:
        """
        if self.id is None:
            raise ValueError("Cannot load line from file without ID!")

        lines_folder = os.getenv('LINES_OBJECTS_FOLDER', '/data/models/lines')
        filepath = os.path.join(lines_folder, f'{self.id}.json')
        if not os.path.isfile(filepath):
            log(
                f"Skipping the load process of line ID {self.id} as the file {filepath} was not found.",
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
        if self.id is None:
            raise ValueError("Cannot persist line to file without ID!")

        lines_folder = os.getenv('LINES_OBJECTS_FOLDER', '/data/models/lines')
        filepath = os.path.join(lines_folder, f'{self.id}.json')
        save_dict_to_json(input_dict=self.serialize(), output_filepath=filepath)
        log(f"Persisted line ID {self.id} to file {filepath}!")


def create_line_from_dict(data_dict: Dict) -> Line:
    """
    Factory method to create a Line model from a given dict
    :param data_dict:
    :return:
    """
    line = Line()
    line.unserialize(data_dict)

    return line
