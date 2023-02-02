import logging
import sys

from logging import Logger, handlers

LOG_FORMAT = (
    "%(asctime)s - %(threadName)s - %(name)s %(levelname)s - %(message)s"  # noqa: E501
)


def init_console(log_level) -> Logger:
    logger = logging.getLogger("app")
    logger.setLevel(log_level)

    standard_formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    console_handler.setFormatter(standard_formatter)

    logger.addHandler(console_handler)

    return logger


def init_file_log(log_level, log_directory: str):
    logger = logging.getLogger("app")

    standard_formatter = logging.Formatter(LOG_FORMAT)

    file_handler = handlers.RotatingFileHandler(f"{log_directory}kouign-amann.log")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(standard_formatter)

    logger.addHandler(file_handler)


def init_console_debug():
    init_console(logging.DEBUG)
