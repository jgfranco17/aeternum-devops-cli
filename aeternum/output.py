import logging
import subprocess
from typing import Optional, Tuple

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


def get_command_string(command: str, args: Optional[Tuple[str]]) -> str:
    cmd_exec = command if not args else f"{command} {' '.join(args)}"
    return cmd_exec


def run_validation_command(command: str, *args: Tuple[str]) -> bool:
    """Returns True if the command is available."""
    try:
        cmd = get_command_string(command, args)
        result = subprocess.run(
            ["/bin/bash", "-c", cmd],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode != 0:
            raise ValueError(f"Command '{cmd}' failed")
        return True
    except (subprocess.CalledProcessError, ValueError):
        return False
