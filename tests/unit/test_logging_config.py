import logging
import os

from dbt_governance.logging_config import (
    DEBUG_LOG_FILE,
    ERROR_LOG_FILE,
    LOG_DIR,
    LOG_FORMAT,
    green,
    logger,
    red,
    yellow,
)


def test_log_directory_exists() -> None:
    """Test that the log directory is created."""
    assert os.path.exists(LOG_DIR), f"Log directory {LOG_DIR} does not exist."


def test_log_file_paths() -> None:
    """Test that the debug and error log file paths are correct."""
    assert DEBUG_LOG_FILE == os.path.join(LOG_DIR, "debug.log"), "DEBUG_LOG_FILE path is incorrect"
    assert ERROR_LOG_FILE == os.path.join(LOG_DIR, "error.log"), "ERROR_LOG_FILE path is incorrect"


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
            if isinstance(h, logging.handlers.RotatingFileHandler) and h.baseFilename == DEBUG_LOG_FILE
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
            if isinstance(h, logging.handlers.RotatingFileHandler) and h.baseFilename == ERROR_LOG_FILE
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
    assert all(LOG_FORMAT in record.message for record in caplog.records), "Log format is incorrect."


def test_log_color_functions() -> None:
    """Test the color output functions."""
    text = "Test message"
    assert green(text) == f"\033[32m{text}\033[0m", "Green function did not produce the correct output"
    assert yellow(text) == f"\033[33m{text}\033[0m", "Yellow function did not produce the correct output"
    assert red(text) == f"\033[31m{text}\033[0m", "Red function did not produce the correct output"
