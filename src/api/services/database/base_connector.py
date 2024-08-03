from abc import ABC, abstractmethod

from api.services.logging import get_logger


class BaseConnector(ABC):
    CONNECTOR_NAME = 'Base DB Connector'

    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.debug(f"Using DB connector '{self.CONNECTOR_NAME}'")

    @abstractmethod
    def get_connection_parameters(self) -> dict:
        raise NotImplementedError()
