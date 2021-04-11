import logging
import sys

LOG_FORMAT = "%(asctime)s - %(threadName)s - %(name)s %(levelname)s - %(message)s"


def init_console(log_level):
    logger = logging.getLogger("app")
    logger.setLevel(log_level)

    standard_formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    console_handler.setFormatter(standard_formatter)

    logger.addHandler(console_handler)


def init_console_debug():
    init_console(logging.DEBUG)
