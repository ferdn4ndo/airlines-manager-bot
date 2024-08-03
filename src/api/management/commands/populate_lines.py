import traceback

from django.core.management.base import BaseCommand, CommandError

from api.services import logging
from api.services.am_lines import LinesFetcherService
from api.services.am_session import AmSessionManager


class Command(BaseCommand):
    help = 'Populate the lines list'

    def __init__(self):
        super().__init__()
        self.logger = logging.get_logger(__name__)

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force the sync of the lines (regardless of last sync date)',
        )

        parser.add_argument(
            '--only-first-page',
            action='store_true',
            help='Sync only the first page of lines',
        )

    def handle(self, *args, **options):
        self.logger.info('Populating lines from the command line interface')

        if options['force']:
            self.logger.info('Sync force was set to true!')

        if options['only_first_page']:
            self.logger.info('Only first page sync option was set to true!')

        session_manager = AmSessionManager()
        service = LinesFetcherService(
            session_manager=session_manager,
            force_sync=options['force'],
            only_first_page=options['only_first_page'],
        )

        try:
            lines = service.fetch_lines()
        except Exception as error:
            self.logger.error(traceback.format_exc())
            raise CommandError(f'An error occurred while running the command: {error}')

        self.logger.info(f'Finished fetching {len(lines)} lines!')
