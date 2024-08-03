from api.models import Airport
from api.services import logging


class AirportService:
    def __init__(self):
        self.logger = logging.get_logger(__name__)

    def get_or_create_airport(
            self,
            iata_code: str = None,
            name: str = None,
            city_name: str = None,
            country_name: str = None,
            country_flag_url: str = None,
            latitude: float = None,
            longitude: float = None,
    ) -> Airport:
        self.logger.debug("Entered method get_or_create_airport")

        airport, created = Airport.objects.get_or_create(iata_code=iata_code)

        airport.name = name
        airport.city_name = city_name
        airport.country_name = country_name
        airport.country_flag_url = country_flag_url
        airport.latitude = latitude
        airport.longitude = longitude

        airport.save()

        if created:
            self.logger.info(f"Created airport {iata_code} ({name}) with ID {airport.id}")

        return airport
