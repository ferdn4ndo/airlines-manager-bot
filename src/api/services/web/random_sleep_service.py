import datetime
import random
import time

from api.services import logging


class RandomSleepService:

    def __init__(self):
        self.logger = logging.get_logger(__name__)

    def wait_random_interval(self, wait_time_min: int, wait_time_max: int, log_output: bool = True):
        """
        Block the execution of the program for a random interval between predetermined limits (in seconds)
        :return:
        """
        self.logger.debug("Entering wait_random_interval method")

        interval = random.randint(int(wait_time_min), int(wait_time_max))

        if log_output:
            self.logger.info(f"Sleeping for {interval} seconds ({str(datetime.timedelta(seconds=interval))})...")

        time.sleep(interval)
