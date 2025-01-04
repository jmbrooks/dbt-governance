import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

import dbt_governance.utils as utils

# Mock constants.PROJECT_NAME
PROJECT_NAME = "dbt-governance"

# Test cases
assemble_dbt_selection_clause_test_cases = [
    # Test select clause only
    ({"select_clause": "model_a model_c model_b", "exclude_clause": None}, " --select model_a model_b model_c"),
    # Test exclude clause only
    ({"select_clause": None, "exclude_clause": "model_x model_z model_y"}, " --exclude model_x model_y model_z"),
    # Test both select and exclude clauses
    (
        {"select_clause": "model_a model_c model_b", "exclude_clause": "model_x model_z model_y"},
        " --select model_a model_b model_c --exclude model_x model_y model_z",
    ),
    # Test empty clauses
    ({"select_clause": None, "exclude_clause": None}, ""),
    # Test whitespace in clauses
    (
        {"select_clause": "  model_a   model_c model_b   ", "exclude_clause": "   model_x  model_z    model_y"},
        " --select model_a model_b model_c --exclude model_x model_y model_z",
    ),
]


@pytest.mark.parametrize("inputs, expected", assemble_dbt_selection_clause_test_cases)
def test_assemble_dbt_selection_clause(inputs: dict, expected: str) -> None:
    """Parameterized test for assemble_dbt_selection_clause."""
    result = utils.assemble_dbt_selection_clause(**inputs)
    assert result == expected


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


def test_validate_path_valid(tmp_path: Path) -> None:
    """Test validate_path with valid paths."""
    # Create a valid path
    valid_path = tmp_path / "valid"
    valid_path.mkdir()

    # Call the function
    result = utils.validate_path(valid_path)

    # Assertions
    assert result == valid_path
    assert isinstance(result, Path)


def test_validate_path_invalid() -> None:
    """Test validate_path with invalid paths."""
    invalid_path = "/invalid/path/to/file"

    with pytest.raises(FileNotFoundError, match=f"Path not found: {invalid_path}"):
        utils.validate_path(invalid_path)


def test_validate_dbt_path_valid(tmp_path: Path) -> None:
    """Test validate_dbt_path with a valid dbt project path."""
    # Create a valid dbt project structure
    valid_path = tmp_path / "dbt_project"
    valid_path.mkdir()
    (valid_path / "dbt_project.yml").write_text("name: test_project\nversion: 1.0.0\n")

    # Call the function
    result = utils.validate_dbt_path(valid_path)

    # Assertions
    assert result == valid_path
    assert isinstance(result, Path)


def test_validate_dbt_path_missing_dbt_project_yml(tmp_path: Path) -> None:
    """Test validate_dbt_path when dbt_project.yml is missing."""
    # Create a directory without dbt_project.yml
    missing_yml_path = tmp_path / "dbt_project"
    missing_yml_path.mkdir()

    with pytest.raises(FileNotFoundError, match=f"dbt_project.yml not found at path: {missing_yml_path}"):
        utils.validate_dbt_path(missing_yml_path)


def test_validate_dbt_path_invalid_path() -> None:
    """Test validate_dbt_path with an invalid path."""
    invalid_path = "/invalid/path/to/dbt_project"

    with pytest.raises(FileNotFoundError, match=f"Path not found: {invalid_path}"):
        utils.validate_dbt_path(invalid_path)


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
    with Path.open(output_file_path, "r") as f:
        written_data = json.load(f)

    assert written_data == sample_data


def test_write_json_result_with_string_path(tmp_path: Path) -> None:
    """Test writing JSON data when output_file_path is a string."""
    sample_data = {"key": "value"}
    output_file_path = tmp_path / "string_path_results.json"  # Pass path as a string

    written_path = utils.write_json_result(sample_data, output_file_path)

    # Verify the output file path
    assert written_path == Path(output_file_path)
    assert Path(output_file_path).exists()

    # Verify the content
    with Path.open(output_file_path, "r") as f:
        written_data = json.load(f)
    assert written_data == sample_data


def test_write_json_result_empty_data(tmp_path: Path) -> None:
    """Test writing empty JSON data."""
    sample_data = {}
    output_file_path = tmp_path / "empty_results.json"

    written_path = utils.write_json_result(sample_data, output_file_path)

    # Verify the output file path
    assert written_path == output_file_path
    assert output_file_path.exists()

    # Verify the content
    with Path.open(output_file_path, "r") as f:
        written_data = json.load(f)
    assert written_data == sample_data  # Should write an empty JSON object


def test_write_json_result_invalid_path() -> None:
    """Test writing to an invalid file path."""
    sample_data = {"key": "value"}
    invalid_path = "/invalid_directory/results.json"  # Non-writable path

    with pytest.raises(OSError, match="No such file or directory"):  # Expect an OSError for invalid path
        utils.write_json_result(sample_data, invalid_path)


def test_write_json_result_non_serializable(tmp_path: Path) -> None:
    """Test writing non-serializable JSON data."""
    sample_data = {"key": object()}  # Non-serializable value
    output_file_path = tmp_path / "non_serializable.json"

    with pytest.raises(TypeError):  # Expect TypeError for non-serializable data
        utils.write_json_result(sample_data, output_file_path)
