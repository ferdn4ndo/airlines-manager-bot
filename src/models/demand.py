from typing import Dict

from models.categorized_value import CategorizedValue
from modules.logger import log, LogLevels


class Demand(CategorizedValue):
    """
    Model class representing the Demand resource (a CategorizedValue class)
    """
    def __str__(self):
        """
        Overrides the original string conversion method to add more information
        :return:
        """
        log("Entering Demand.__str__ method", LogLevels.LOG_LEVEL_DEBUG)

        return '{} + {} + {} Pax ({} total) | {} T'.format(
            self.economic,
            self.executive,
            self.first_class,
            self.get_total_pax(),
            self.cargo
        )

    def get_total_pax(self) -> int:
        """
        Helper function to retrieve the total amount of passengers (summing economic, executive and first class pax)
        :return:
        """
        log("Entering Demand.persist_to_file method", LogLevels.LOG_LEVEL_DEBUG)

        return self.economic + self.executive + self.first_class


def create_demand_from_dict(data_dict: Dict) -> Demand:
    """
    Factory method to create a Demand model from a given dict
    :param data_dict:
    :return:
    """
    log("Entering create_demand_from_dict method", LogLevels.LOG_LEVEL_DEBUG)

    demand = Demand()
    demand.unserialize(data_dict)

    return demand
