import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

import dbt_governance.utils as utils


def test_get_utc_iso_timestamp() -> None:
    """Test that get_utc_iso_timestamp returns a valid ISO 8601 timestamp with millisecond precision."""
    current_timestamp = utils.get_utc_iso_timestamp()

    # Ensure the returned timestamp is a string
    assert isinstance(current_timestamp, str)

    # Parse the returned timestamp to ensure it's valid
    parsed_time = datetime.strptime(current_timestamp, "%Y-%m-%d %H:%M:%S.%f%z")

    # Verify that the parsed time is in UTC
    assert parsed_time.tzinfo == timezone.utc

    # Verify that the precision includes milliseconds
    assert len(current_timestamp.split(".")[-1]) >= 3


def test_get_uuid() -> None:
    """Test that get_uuid returns a valid UUID string."""
    uuid = utils.get_uuid()

    # Ensure the returned value is a string
    assert isinstance(uuid, str)

    # Validate that the UUID matches the standard UUID format using a regex
    uuid_regex = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$", re.IGNORECASE)
    assert uuid_regex.match(uuid), f"Invalid UUID format: {uuid}"


def test_write_json_result(tmp_path: Path) -> None:
    """Test that write_json_result writes JSON data to the correct file."""
    # Sample data to write
    sample_data = {
        "summary": {"passed": 2, "failed": 1},
        "details": [
            {"rule": "Primary Key Test", "status": "passed", "reason": None},
            {"rule": "Owner Metadata", "status": "failed", "reason": "Missing owner meta property"},
        ],
    }

    # Define the output file path in the temporary directory
    output_file_path = tmp_path / "results.json"

    # Call the function
    written_path = utils.write_json_result(sample_data, output_file_path)

    # Ensure the returned path is correct
    assert written_path == output_file_path

    # Ensure the file was created
    assert output_file_path.exists()

    # Read the file and validate its content
    with open(output_file_path, "r") as f:
        written_data = json.load(f)

    assert written_data == sample_data


def test_write_json_result_with_string_path(tmp_path: Path) -> None:
    """Test writing JSON data when output_file_path is a string."""
    sample_data = {"key": "value"}
    output_file_path = str(tmp_path / "string_path_results.json")  # Pass path as a string

    written_path = utils.write_json_result(sample_data, output_file_path)

    # Verify the output file path
    assert written_path == Path(output_file_path)
    assert Path(output_file_path).exists()

    # Verify the content
    with open(output_file_path, "r") as f:
        written_data = json.load(f)
    assert written_data == sample_data


def test_write_json_result_empty_data(tmp_path: Path) -> None:
    """Test writing empty JSON data."""
    sample_data = {}  # type: ignore
    output_file_path = tmp_path / "empty_results.json"

    written_path = utils.write_json_result(sample_data, output_file_path)

    # Verify the output file path
    assert written_path == output_file_path
    assert output_file_path.exists()

    # Verify the content
    with open(output_file_path, "r") as f:
        written_data = json.load(f)
    assert written_data == sample_data  # Should write an empty JSON object


def test_write_json_result_invalid_path() -> None:
    """Test writing to an invalid file path."""
    sample_data = {"key": "value"}
    invalid_path = "/invalid_directory/results.json"  # Non-writable path

    with pytest.raises(OSError):  # Expect an OSError for invalid path
        utils.write_json_result(sample_data, invalid_path)


def test_write_json_result_non_serializable(tmp_path: Path) -> None:
    """Test writing non-serializable JSON data."""
    sample_data = {"key": object()}  # Non-serializable value
    output_file_path = tmp_path / "non_serializable.json"

    with pytest.raises(TypeError):  # Expect TypeError for non-serializable data
        utils.write_json_result(sample_data, output_file_path)
