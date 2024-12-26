import logging
import os
import sys
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path

import colorama

# Log file paths
LOG_DIR = Path("~/dbt-governance-logs").expanduser()
DEBUG_LOG_FILE = LOG_DIR / "debug.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"

if sys.platform == "win32" and (not os.getenv("TERM") or os.getenv("TERM") == "None"):
    colorama.init(wrap=True)


class Color(Enum):
    """Enumeration of color codes for console output.

    Attributes:
        RED: ANSI color code for red text.
        GREEN: ANSI color code for green text.
        YELLOW: ANSI color code for yellow text.
        RESET_ALL: ANSI color code to reset all text formatting
    """

    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    RESET_ALL = colorama.Style.RESET_ALL


# Base log directory
Path.mkdir(LOG_DIR, exist_ok=True, parents=True)

# Logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configure debug log handler (rotating)
debug_handler = RotatingFileHandler(DEBUG_LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Configure error log handler (rotating)
error_handler = RotatingFileHandler(ERROR_LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=2)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Configure console log handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Configure the root logger
logging.basicConfig(
    level=logging.DEBUG,  # Root logger level
    handlers=[debug_handler, error_handler, console_handler],  # Handlers
)

# Create a logger for the package
logger = logging.getLogger("dbt_governance")


def return_in_color(text: str, color_code: Color, use_color: bool = True) -> str:
    """Output the given text in the specified color, so long as `use_color` is set to True (the default)."""
    return "{}{}{}".format(color_code.value, text, Color.RESET_ALL.value) if use_color else text


def green(text: str) -> str:
    """Output given text in green."""
    return return_in_color(text, Color.GREEN)


def yellow(text: str) -> str:
    """Output given text in yellow."""
    return return_in_color(text, Color.YELLOW)


def red(text: str) -> str:
    """Output given text in red."""
    return return_in_color(text, Color.RED)
