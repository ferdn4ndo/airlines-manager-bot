from api.exception import InternalServerError
from api.services.env import variables

from .base_connector import BaseConnector
from .sqlite_connector import SqliteConnector
from .postgres_connector import PostgresConnector


def create_connector_from_env() -> BaseConnector:
    db_engine = variables.get('DB_ENGINE')
    if db_engine == 'sqlite':
        return SqliteConnector()
    elif db_engine == 'postgres':
        return PostgresConnector()

    raise InternalServerError(f'Unknown database engine "{db_engine}"')
