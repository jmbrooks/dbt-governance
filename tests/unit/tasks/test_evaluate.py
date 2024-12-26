import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from dbt_governance.tasks.evaluate import evaluate_task
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.severity import Severity
from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus
from dbt_governance.structures.governance_result import GovernanceResult


@patch("dbt_governance.tasks.evaluate.DbtProject")
@patch("dbt_governance.tasks.evaluate.utils.get_utc_iso_timestamp", return_value="2024-01-01T00:00:00Z")
def test_evaluate_task_valid_rules(mock_get_utc_iso_timestamp, mock_dbt_project, tmp_path: Path) -> None:
    """Test evaluate_task with valid rules and a valid dbt project."""
    # Mock manifest.json path
    manifest_path = tmp_path / "dbt_project/target/manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("{}")  # Mock manifest content

    # Mock dbt project behavior
    mock_dbt_project.return_value.dbt_version = "1.9.0"
    mock_dbt_project.return_value.generated_at = "2024-01-01T00:00:00Z"
    mock_dbt_project.return_value.load_manifest.return_value = {"nodes": {}}

    # Mock rules
    rules = [
        GovernanceRule(
            name="Primary Key Test",
            type="data",
            description="Ensure primary key tests are defined.",
            severity=Severity.HIGH,
            enabled=True,
        ),
        GovernanceRule(
            name="Owner Metadata",
            type="metadata",
            description="Ensure all models have an owner defined.",
            severity=Severity.MEDIUM,
            enabled=True,
        ),
    ]

    # Call the function
    result = evaluate_task(
        rules=rules,
        project_paths=[tmp_path / "dbt_project"],
        check_uuid="123e4567-e89b-12d3-a456-426614174000",
        dbt_governance_version="0.1.0",
    )

    # Assertions
    assert isinstance(result, GovernanceResult)
    assert result.metadata.generated_at == "2024-01-01T00:00:00Z"
    assert result.metadata.dbt_governance_version == "0.1.0"
    assert result.metadata.result_uuid == "123e4567-e89b-12d3-a456-426614174000"
    assert result.summary.total_evaluations == 0  # No validations executed
    mock_dbt_project.assert_called_once_with(project_path="/path/to/dbt_project")
    mock_get_utc_iso_timestamp.assert_called_once()


@patch("dbt_governance.tasks.evaluate.DbtProject")
def test_evaluate_task_no_enabled_rules(mock_dbt_project) -> None:
    """Test evaluate_task with no enabled rules."""
    mock_dbt_project.return_value.load_manifest.return_value = {"nodes": {}}

    # Mock rules
    rules = [
        GovernanceRule(
            name="Disabled Rule",
            type="data",
            description="A rule that is disabled.",
            severity=Severity.LOW,
            enabled=False,
        )
    ]

    # Call the function
    result = evaluate_task(
        rules=rules,
        project_paths=["/path/to/dbt_project"],
        check_uuid="123e4567-e89b-12d3-a456-426614174000",
        dbt_governance_version="0.1.0",
    )

    # Assertions
    assert result.summary.total_evaluations == 0
    assert len(result.results) == 0


@patch("dbt_governance.tasks.evaluate.DbtProject")
def test_evaluate_task_invalid_manifest(mock_dbt_project) -> None:
    """Test evaluate_task with an invalid manifest."""
    mock_dbt_project.return_value.load_manifest.side_effect = FileNotFoundError("Mocked manifest not found.")

    # Mock rules
    rules = [
        GovernanceRule(
            name="Primary Key Test",
            type="data",
            description="Ensure primary key tests are defined.",
            severity=Severity.HIGH,
            enabled=True,
        )
    ]

    with pytest.raises(FileNotFoundError, match="Mocked manifest not found."):
        evaluate_task(
            rules=rules,
            project_paths=["/path/to/dbt_project"],
            check_uuid="123e4567-e89b-12d3-a456-426614174000",
            dbt_governance_version="0.1.0",
        )
