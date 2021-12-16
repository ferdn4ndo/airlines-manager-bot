from typing import Dict


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
        self.unserialize(kwargs)

    def serialize(self) -> Dict:
        """
        Writes the model as a dict
        :return:
        """
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
        if not all([hasattr(self, field) for field in data_dict.keys()]):
            raise ValueError('Not all fields are valid!')

        for field in data_dict.keys():
            setattr(self, field, data_dict[field])

        return self
