from typing import Dict

from models.categorized_value import CategorizedValue
from modules.logger import log, LogLevels


class Price(CategorizedValue):
    """
    Model class representing the Price resource
    """
    def __str__(self):
        log("Entering Price.__str__ method", LogLevels.LOG_LEVEL_DEBUG)

        total = self.economic + self.executive + self.first_class + self.cargo

        return f'$ {total}'


def create_price_from_dict(data_dict: Dict) -> Price:
    """
    Factory method to create a Price model from a given dict
    :param data_dict:
    :return:
    """
    log("Entering create_price_from_dict method", LogLevels.LOG_LEVEL_DEBUG)

    price = Price()
    price.unserialize(data_dict)

    return price
