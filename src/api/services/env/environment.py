from api.exception import InternalServerError

from .env_variable import EnvVariable


class Environment:
    variables = {}

    def set(self, key: str, **kwargs):
        self.variables[key] = EnvVariable(key=key, **kwargs)

    def get(self, key: str):
        if key not in self.variables:
            raise InternalServerError(f'The key "{key}" is not set in the environment')

        return self.variables[key].get_value()
