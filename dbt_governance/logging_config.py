import logging
from logging.handlers import RotatingFileHandler
import os

from dbt_governance.constants import LOG_DIR

# Base log directory
os.makedirs(LOG_DIR, exist_ok=True)  # Create the directory if it doesn't exist

# Log file paths
DEBUG_LOG_FILE = os.path.join(LOG_DIR, "debug.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")

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
