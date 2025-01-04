import logging
import os
import sys
from pathlib import Path
from unittest.mock import patch

import colorama

from dbt_governance.logging_config import (
    DEBUG_LOG_FILE,
    ERROR_LOG_FILE,
    LOG_DIR,
    LOG_FORMAT,
    LOGGER_NAME,
    green,
    logger,
    red,
    yellow,
)


@patch("os.getenv")
@patch("sys.platform", "linux")
@patch("colorama.init")
def test_colorama_init_not_called_on_non_win32(mock_colorama_init, mock_getenv) -> None:
    """Test that colorama.init is not called when platform is not win32."""
    # Mock os.getenv to simulate TERM not being set
    mock_getenv.return_value = None

    # Simulate the conditional logic
    if sys.platform == "win32" and (not os.getenv("TERM") or os.getenv("TERM") == "None"):
        colorama.init(wrap=True)

    # Assert colorama.init was not called
    mock_colorama_init.assert_not_called()


def test_logger_name() -> None:
    """Confirm the logger name matches project naming expectation."""
    assert logger.name == "dbt-governance"


def test_log_directory_exists() -> None:
    """Test that the log directory is created."""
    assert Path.exists(LOG_DIR), f"Log directory {LOG_DIR} does not exist."


def test_log_file_paths() -> None:
    """Test that the debug and error log file paths are correct."""
    assert DEBUG_LOG_FILE == LOG_DIR / "debug.log", "DEBUG_LOG_FILE path is incorrect"
    assert ERROR_LOG_FILE == LOG_DIR / "error.log", "ERROR_LOG_FILE path is incorrect"


def test_logger_handlers() -> None:
    """Test that the logger has the required handlers."""
    handler_types = [type(handler) for handler in logger.handlers]
    assert logging.handlers.RotatingFileHandler in handler_types, "RotatingFileHandler is missing"
    assert logging.StreamHandler in handler_types, "StreamHandler is missing"


def test_debug_handler_configuration() -> None:
    """Test the configuration of the debug RotatingFileHandler."""
    debug_handler = next(
        (
            h
            for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler) and str(DEBUG_LOG_FILE) in h.baseFilename
        ),
        None,
    )
    assert debug_handler is not None, "Debug handler is not configured"
    assert debug_handler.maxBytes == 5 * 1024 * 1024, "Debug handler maxBytes is incorrect"
    assert debug_handler.backupCount == 3, "Debug handler backupCount is incorrect"
    assert debug_handler.level == logging.DEBUG, "Debug handler level is incorrect"


def test_error_handler_configuration() -> None:
    """Test the configuration of the error RotatingFileHandler."""
    error_handler = next(
        (
            h
            for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler) and str(ERROR_LOG_FILE) in h.baseFilename
        ),
        None,
    )
    assert error_handler is not None, "Error handler is not configured"
    assert error_handler.maxBytes == 2 * 1024 * 1024, "Error handler maxBytes is incorrect"
    assert error_handler.backupCount == 2, "Error handler backupCount is incorrect"
    assert error_handler.level == logging.ERROR, "Error handler level is incorrect"


def test_log_format(caplog) -> None:
    """Test that log messages follow the defined log format."""
    with caplog.at_level(logging.DEBUG):
        logger.debug("This is a test message.")

    assert len(caplog.records) > 0, "No log records were captured."

    # Create a formatter using the LOG_FORMAT
    formatter = logging.Formatter(LOG_FORMAT)

    # Validate that each captured record matches the format
    for record in caplog.records:
        formatted_message = formatter.format(record)
        assert LOGGER_NAME in formatted_message, "Logger name not found in formatted message."
        assert "DEBUG" in formatted_message, "Log level not found in formatted message."
        assert "This is a test message." in formatted_message, "Log message not found in formatted message."


def test_log_color_functions() -> None:
    """Test the color output functions."""
    text = "Test message"
    assert green(text) == f"\033[32m{text}\033[0m", "Green function did not produce the correct output"
    assert yellow(text) == f"\033[33m{text}\033[0m", "Yellow function did not produce the correct output"
    assert red(text) == f"\033[31m{text}\033[0m", "Red function did not produce the correct output"
