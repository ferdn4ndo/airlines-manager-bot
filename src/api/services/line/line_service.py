from api.models import Line
from api.services import logging


class LineService:
    def __init__(self):
        self.logger = logging.get_logger(__name__)

    def get_or_create_line_by_am_id(self, am_id: int):
        self.logger.debug("Entered method get_or_create_airport")
        line, created = Line.objects.get_or_create(am_id=am_id)

        if created:
            self.logger.info(f"Created line for AM ID #{am_id} with internal ID {line.id}")

        return line
