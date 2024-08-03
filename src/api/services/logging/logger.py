import logging
import inspect

from api.services.env import variables

MAIN_LOGGER_NAME = 'api'


def get_logger(name: str = MAIN_LOGGER_NAME) -> logging.Logger:
    logger = logging.getLogger(name)

    return logger

    # env_mode = variables.get('ENV_MODE')
    # log_level = logging.DEBUG if env_mode == 'dev' else logging.WARNING
    # logger.setLevel(log_level)
    #
    # # Get the previous frame in the stack, otherwise it would
    # # be this function!!!
    # func = inspect.currentframe().f_back.f_code
    #
    # logger_handler = logging.NullHandler()
    # logger_handler.setLevel(log_level)
    # logger_formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - {} ({}:{}) - %(message)s'.format(
    #         func.co_name,
    #         func.co_filename,
    #         func.co_firstlineno
    #     )
    # )
    # logger_handler.setFormatter(logger_formatter)
    # logger.addHandler(logger_handler)
    #
    # return logger
