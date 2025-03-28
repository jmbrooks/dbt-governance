import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union
from uuid import uuid4


def assemble_dbt_selection_clause(select_clause: Optional[str] = None, exclude_clause: Optional[str] = None) -> str:
    """Assemble a dbt selection clause from select and exclude clauses.

    Args:
        select_clause: dbt select clause to assemble.
        exclude_clause: dbt exclude clause to assemble.

    Returns:
        The assembled dbt selection clause as a string.
    """
    selection_clause = ""
    sorted_select_clause = ""
    sorted_exclude_clause = ""
    if select_clause or exclude_clause:
        if select_clause:
            selections = select_clause.split()
            sorted_selections = sorted(selections)
            sorted_select_clause = " ".join(sorted_selections)

        if exclude_clause:
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


def validate_path(path: Union[str, Path]) -> Path:
    """Validate a path string or Path object, returning a Path object.

    Args:
        path (Union[str, Path]): Path to confirm exists (is valid).

    Returns:
        Path: Path object of the valid path, if it is indeed valid.

    Raises:
        FileNotFoundError: If path does not exist.
    """
    if not Path(path) or not Path(path).exists():
        raise FileNotFoundError(f"Path not found: {path}")
    return Path(path) if isinstance(path, str) else path


def validate_dbt_path(path: Union[str, Path]) -> Path:
    """Validate a dbt project path string or Path object, returning a Path object.

    Args:
        path (Union[str, Path]): dbt project path.

    Returns:
        Path: The dbt project Path, if valid.

    Raises:
        FileNotFoundError: If the dbt project path does not exist.
    """
    path = validate_path(path)
    if not (path / "dbt_project.yml").exists():
        raise FileNotFoundError(f"dbt_project.yml not found at path: {path}")
    return path


def write_json_result(results_data: dict[str, Any], output_file_path: Union[str, Path]) -> Path:
    """Write data to JSON file with consistent formatting, and return the successfully-written-to output path.

    Args:
        results_data (dict[str, Any]): Dictionary of all results of the dbt-governance run.
        output_file_path (Union[str, Path]): Path to the output results file.

    Returns:
        Path: Path object for the output results file.
    """
    output_file_path = Path(output_file_path)
    with output_file_path.open(mode="w") as output_file:
        json.dump(results_data, output_file, indent=4)
    return Path(output_file_path)
