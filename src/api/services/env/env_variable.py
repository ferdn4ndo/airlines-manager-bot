import os

from api.exception import InternalServerError


class EnvVariable:
    def __init__(self, key: str, **kwargs):
        self.key = key
        self.default = kwargs['default'] if 'default' in kwargs else None
        self.required = kwargs['required'] if 'required' in kwargs else False
        self.description = kwargs['description'] if 'description' in kwargs else ""

    def __str__(self):
        return self.get_value()

    def get_value(self):
        if self.required and self.key not in os.environ and self.default is None:
            raise InternalServerError(f"The required environment variable '{self.key}' is not set!")

        return os.getenv(self.key, self.default)
