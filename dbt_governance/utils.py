import json
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, Union
from uuid import uuid4

import dbt_governance.constants as constants


def assemble_dbt_selection_clause(select_clause: Optional[str] = None, exclude_clause: Optional[str] = None) -> str:
    """Assemble a dbt selection clause from select and exclude clauses."""
    selection_clause = ""
    if select_clause or exclude_clause:
        selections = select_clause.split()
        sorted_selections = sorted(selections)
        sorted_select_clause = " ".join(sorted_selections)

        exclusions = exclude_clause.split()
        sorted_exclusions = sorted(exclusions)
        sorted_exclude_clause = " ".join(sorted_exclusions)

        if sorted_select_clause:
            selection_clause += f" --select {sorted_select_clause}"
        if sorted_exclude_clause:
            selection_clause += f" --exclude {sorted_exclude_clause}"
    return selection_clause


def get_utc_iso_timestamp() -> str:
    """Return the current UTC timestamp, with millisecond precision, in ISO format."""
    return datetime.now(timezone.utc).isoformat(sep=" ", timespec="milliseconds")


def get_uuid() -> str:
    """Return a string universally unique identifier (UUID)."""
    return str(uuid4())


def track_runtime(func: Callable) -> Callable[[tuple[Any, ...], dict[str, Any]], tuple[Any, float]]:
    """Decorator to measure the runtime of a function and print it."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Calculate runtime in seconds
        runtime_seconds = end_time - start_time

        # Format the runtime for stdout
        minutes, seconds = divmod(runtime_seconds, 60)
        runtime_message = (
            f"Finished {constants.PROJECT_NAME} evaluation in {int(minutes)} minutes and {seconds:.2f} seconds "
            f"({runtime_seconds:.2f}s)."
        )
        # logger.info(f"\nFinished {constants.PROJECT_NAME} evaluation in {int(minutes)} minutes and {seconds:.2f} "
        #             f"seconds ({runtime_seconds:.2f}s).")

        # Return both the result and runtime
        return result, runtime_seconds, runtime_message

    return wrapper


def validate_path(path: Union[str, Path]) -> Path:
    """Validate a path string or Path object, returning a Path object."""
    if not Path(path) or not Path(path).exists():
        raise FileNotFoundError(f"Path not found: {path}")
    return Path(path) if isinstance(path, str) else path


def validate_dbt_path(path: Union[str, Path]) -> Path:
    """Validate a dbt project path string or Path object, returning a Path object."""
    path = validate_path(path)
    if not (path / "dbt_project.yml").exists():
        raise FileNotFoundError(f"dbt_project.yml not found at path: {path}")
    return path


def write_json_result(results_data: dict[str, Any], output_file_path: Union[str, Path]) -> Path:
    """Write data to JSON file with consistent formatting, and return the successfully-written-to output path."""
    output_file_path = Path(output_file_path)
    with output_file_path.open("w") as output_file:
        json.dump(results_data, output_file, indent=4)
    return Path(output_file_path)
