from typing import Dict

from modules.logger import log, LogLevels


class BaseModel:
    """
    Base model class to be inherited by the other project models
    """
    serializable_fields = []

    def __init__(self, **kwargs):
        """
        Base model constructor
        :param kwargs:
        """
        log("Instantiating BaseModel class", LogLevels.LOG_LEVEL_DEBUG)
        self.unserialize(kwargs)

    def serialize(self) -> Dict:
        """
        Writes the model as a dict
        :return:
        """
        log("Entering BaseModel.serialize method", LogLevels.LOG_LEVEL_DEBUG)

        serialized_dict = {}

        for field in self.serializable_fields:
            serialized_dict[field] = getattr(self, field) if hasattr(self, field) else None

        return serialized_dict

    def unserialize(self, data_dict: Dict):
        """
        Loads the model from a dict
        :param data_dict:
        :return:
        """
        log("Entering BaseModel.unserialize method", LogLevels.LOG_LEVEL_DEBUG)

        if not all([hasattr(self, field) for field in data_dict.keys()]):
            raise ValueError('Not all fields are valid!')

        for field in data_dict.keys():
            setattr(self, field, data_dict[field])

        return self
