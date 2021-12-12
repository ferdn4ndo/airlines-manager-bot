import datetime
import os
import random
import subprocess
import time
from typing import List

from .airplanes import fetch_all_airplanes
from .card_holder import get_free_card_holder_if_available
from .lines import fetch_all_lines
from .logger import log, LogLevels
from .login import get_cookies
from .travel_cards_wheel import spin_travel_cards_wheel_if_available
from .workshop import get_free_workshop_items


def execute_from_arguments(arguments: List):
    """
    Execute the program based on the given arguments
    :param arguments:
    :return:
    """
    if len(arguments) == 0:
        execute_infinite_loop()
        return

    if arguments == ['-d'] or arguments == ['--daemon']:
        log("Running as a daemon")
        subprocess.run(['python3', 'main.py', '-a'])
        return

    log("Unknown set of arguments ['{}']!".format("','".join(arguments)), LogLevels.LOG_LEVEL_ERROR)


def execute_infinite_loop():
    """
    Execute the main tasks in an eternal loop, waiting a random interval between each of the executions
    :return:
    """
    while True:
        try:
            execute_tasks()
            wait_random_interval()
        except ReferenceError:
            log("An error occurred when parsing a page, executing again in 10 seconds...")
            time.sleep(10)


def wait_random_interval():
    """
    Block the execution of the program for a random interval between predetermined limits
    :return:
    """
    wait_time_min = os.environ['WAIT_TIME_MIN'] if 'WAIT_TIME_MIN' in os.environ else (60*60*5)
    wait_time_max = os.environ['WAIT_TIME_MAX'] if 'WAIT_TIME_MAX' in os.environ else (60*60*8)
    interval = random.randint(int(wait_time_min), int(wait_time_max))
    log("Sleeping for {} seconds ({})...".format(interval, str(datetime.timedelta(seconds=interval))))
    time.sleep(interval)


def execute_tasks():
    """
    Main execution block of the regular tasks
    :return:
    """
    log("")
    log("Executing main tasks!")

    cookies = get_cookies()

    # Fetch the airplanes
    fetch_all_airplanes(cookies=cookies)

    # Fetch the lines
    fetch_all_lines(cookies=cookies)

    # Travel cards wheel
    spin_travel_cards_wheel_if_available(cookies=cookies)

    # Free card holder
    get_free_card_holder_if_available(cookies=cookies)

    # Free workshop items
    get_free_workshop_items(cookies)
