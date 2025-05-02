import logging
from pathlib import Path
import sys

from logging import Logger, handlers

from isort import file

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


def init_file_log(log_level, log_file: str):
    logger = logging.getLogger("app")

    standard_formatter = logging.Formatter(LOG_FORMAT)
    file_handler = logging.FileHandler(filename=log_file, mode="a+")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(standard_formatter)

    logger.addHandler(file_handler)


def init_console_debug():
    init_console(logging.DEBUG)
