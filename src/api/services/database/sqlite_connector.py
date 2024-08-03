from api.services.env import variables

from .base_connector import BaseConnector


class SqliteConnector(BaseConnector):
    CONNECTOR_NAME = 'SQLite DB Connector'

    def get_connection_parameters(self) -> dict:
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': variables.get('SQLITE_FILEPATH'),
        }
