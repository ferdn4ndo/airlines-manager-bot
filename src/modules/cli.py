import datetime
import os
import subprocess
import time

from typing import List

from modules.airplanes import fetch_all_airplanes_list
from modules.card_holder import get_free_card_holder_if_available
from modules.lines import fetch_all_lines_list
from modules.lines_data import update_all_lines_data
from modules.logger import log, LogLevels
from modules.session_manager import SessionManager
from modules.time import wait_random_interval
from modules.travel_cards_wheel import spin_travel_cards_wheel_if_available
from modules.workshop import get_free_workshop_items


def execute_from_arguments(arguments: List):
    """
    Execute the program based on the given arguments
    :param arguments:
    :return:
    """
    log(f"Executing from arguments: [ {' , '.join(arguments)} ]", LogLevels.LOG_LEVEL_DEBUG)
    if len(arguments) == 0:
        execute_infinite_loop()
        return

    if arguments == ['-d'] or arguments == ['--daemon']:
        log("CLI: Running as a daemon")
        subprocess.run(['python3', 'main.py', '-a'])
        return

    if arguments == ['-u'] or arguments == ['--update-lines-ticket']:
        log("CLI: Updating lines ticket values")
        session_manager = SessionManager()
        update_all_lines_data(session_manager=session_manager)
        return

    log("Unknown set of arguments ['{}']!".format("','".join(arguments)), LogLevels.LOG_LEVEL_ERROR)


def execute_infinite_loop():
    """
    Execute the main tasks in an eternal loop, waiting a random interval between each of the executions
    :return:
    """
    log("Entering execute_infinite_loop method", LogLevels.LOG_LEVEL_DEBUG)
    while True:
        try:
            execute_tasks()
            wait_random_interval(
                wait_time_min=os.getenv('WAIT_TIME_MIN', 60*60*5),
                wait_time_max=os.getenv('WAIT_TIME_MAX', 60*60*8),
            )
        except ReferenceError:
            log("An error occurred when parsing a page, executing again in 10 seconds...")
            time.sleep(10)


def execute_tasks():
    """
    Main execution block of the regular tasks
    :return:
    """
    log("")
    log("Executing main tasks!")

    start_time = time.time()

    session_manager = SessionManager()

    # Travel cards wheel
    spin_travel_cards_wheel_if_available(session_manager=session_manager)

    # Free card holder
    get_free_card_holder_if_available(session_manager=session_manager)

    # Free workshop items
    get_free_workshop_items(session_manager=session_manager)

    # Fetch the airplanes
    fetch_all_airplanes_list(session_manager=session_manager)

    # Fetch the lines
    fetch_all_lines_list(session_manager=session_manager)

    total_interval = round(time.time() - start_time)
    total_timedelta = datetime.timedelta(seconds=total_interval)

    log(f"Finished executing main tasks! Total execution time: {total_interval} seconds ({str(total_timedelta)})")
