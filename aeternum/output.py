import logging
from typing import Iterable

import click
from colorama import Fore, Style


class ColorHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        colors = {
            logging.DEBUG: Fore.CYAN,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.RED,
        }
        color = colors.get(record.levelno, Fore.WHITE)
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        super().emit(record)
