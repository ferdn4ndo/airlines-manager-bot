import datetime
import os

from typing import List

from models.line import Line
from modules.lines_data import update_line_data
from modules.lines_summary import fetch_lines_summary
from modules.logger import log, LogLevels
from modules.session_manager import SessionManager


def fetch_all_lines_list(session_manager: SessionManager) -> List:
    """
    Retrieves a list with all the airplanes registered in the account (and their summarized data), saving the output
    to a CSV file.
    :param session_manager:
    :return:
    """
    log("Entering fetch_all_lines_list method", LogLevels.LOG_LEVEL_DEBUG)
    lines_summary = fetch_lines_summary(session_manager=session_manager)
    lines = [create_line_object(line_id=line['id'], session_manager=session_manager) for line in lines_summary]
    lines_objects_folder = os.getenv('LINES_OBJECTS_FOLDER', '/data/models/lines')
    log(f"Finished fetching {len(lines_summary)} lines! (objects saved to folder {lines_objects_folder})")

    return lines


def create_line_object(line_id: int, session_manager: SessionManager) -> Line:
    """
    Create the Line object and updates it with the given ID
    :param session_manager:
    :param line_id:
    :return:
    """
    log("Entering create_line_object method", LogLevels.LOG_LEVEL_DEBUG)
    line = Line(id=line_id)

    update_frequency_days = int(os.getenv('LINE_UPDATE_INTERVAL_DAYS', 2))
    delta_days = (datetime.datetime.now() - line.last_updated_at).days if line.last_updated_at is not None else 0
    if line.last_updated_at is not None and delta_days < update_frequency_days:
        log(
            "No need to update line {} (ID: {}) as only {} day(s) have passed since last update (expected {})".format(
                line.name,
                line.id,
                delta_days,
                update_frequency_days
            ),
            LogLevels.LOG_LEVEL_NOTICE
        )
        return line

    update_line_data(line=line, session_manager=session_manager)

    return line
