import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Union
from uuid import uuid4


def get_utc_iso_timestamp() -> str:
    """Return the current UTC timestamp, with millisecond precision, in ISO format."""
    return datetime.now(timezone.utc).isoformat(sep=" ", timespec="milliseconds")


def get_uuid() -> str:
    """Return a string universally unique identifier (UUID)."""
    return str(uuid4())


def write_json_result(results_data: Dict[str, Any], output_file_path: Union[str, Path]) -> Path:
    """Write data to JSON file with consistent formatting, and return the successfully-written-to output path."""
    output_file_path = Path(output_file_path)
    with output_file_path.open("w") as output_file:
        json.dump(results_data, output_file, indent=4)
    return Path(output_file_path)
