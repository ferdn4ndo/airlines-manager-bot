import datetime
import random
import time

from modules.logger import log, LogLevels


def wait_random_interval(wait_time_min: int, wait_time_max: int, log_output: bool = True):
    """
    Block the execution of the program for a random interval between predetermined limits (in seconds)
    :return:
    """
    log("Entering wait_random_interval method", LogLevels.LOG_LEVEL_DEBUG)

    interval = random.randint(int(wait_time_min), int(wait_time_max))

    if log_output:
        log(f"Sleeping for {interval} seconds ({str(datetime.timedelta(seconds=interval))})...")

    time.sleep(interval)
