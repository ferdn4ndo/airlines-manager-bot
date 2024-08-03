from api.services.env import variables

from .base_connector import BaseConnector


class PostgresConnector(BaseConnector):
    CONNECTOR_NAME = 'Postgres DB Connector'

    def get_connection_parameters(self) -> dict:
        return {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': variables.get('POSTGRES_DB'),
            'USER': variables.get('POSTGRES_USER'),
            'PASSWORD': variables.get('POSTGRES_PASS'),
            'HOST': variables.get('POSTGRES_HOST'),
            'PORT': variables.get('POSTGRES_PORT'),
        }
