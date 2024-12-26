from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

import dbt_governance.constants as constants
from dbt_governance import __version__
from dbt_governance.cli import cli as dbt_governance_cli
from dbt_governance.structures.governance_result import (
    GovernanceResult,
    GovernanceResultMetadata,
    GovernanceResultSummary,
)
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.severity import Severity
from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def test_version_option() -> None:
    """Test that the `--version` and `-V` options output the correct version."""
    runner = CliRunner()

    # Test --version
    result = runner.invoke(dbt_governance_cli, ["--version"])
    assert result.exit_code == 0
    assert f"dbt-governance, version {__version__}" in result.output

    # Test -V (short flag)
    result = runner.invoke(dbt_governance_cli, ["-V"])
    assert result.exit_code == 0
    assert "dbt-governance, version 0.1.0" in result.output


@patch("dbt_governance.cli.evaluate_rules")
@patch("dbt_governance.cli.load_rules")
def test_check_command(mock_load_rules, mock_evaluate_rules, tmp_path: Path) -> None:
    """Test the `check` command."""
    runner = CliRunner()

    # Create a temporary rules.yml file
    rules_file = tmp_path / constants.DEFAULT_RULES_FILE_NAME
    rules_file.write_text(
        """
    - name: Owner Metadata
      severity: medium
    """
    )

    # Mock return values
    mock_load_rules.return_value = [{"name": "Owner Metadata", "severity": "medium"}]

    # Create real GovernanceResult components
    details = [
        ValidationResult(
            rule_name="Owner Metadata",
            status=ValidationStatus.PASSED,
            dbt_project_path="path/to/dbt/project",
            resource_type="model",
            unique_id="model.my_project.dim_date",
            reason=None,
        )
    ]
    summary = GovernanceResultSummary(
        total_evaluations=1,
        total_passed=1,
        total_failed=0,
    )
    metadata = GovernanceResultMetadata(
        generated_at="2024-12-09T12:00:00Z",
        result_uuid="test-uuid",
        dbt_governance_version="0.1.0",
    )

    # Create a real GovernanceResult object
    results = GovernanceResult(summary=summary, metadata=metadata, results=details)
    mock_evaluate_rules.return_value = results

    # Invoke the CLI
    result = runner.invoke(
        dbt_governance_cli,
        [
            "check",
            "--project-path",
            str(tmp_path),
            "--rules-file",
            str(rules_file),
        ],
    )

    # Assertions
    assert result.exit_code == 0, f"Unexpected output: {result.output}"
    assert "Governance Check Results:" in result.output
    assert "Passed: 1" in result.output
    assert "Failed: 0" in result.output

    # Verify mocks
    mock_load_rules.assert_called_once_with(str(rules_file))
    mock_evaluate_rules.assert_called_once()


@patch("dbt_governance.cli.evaluate_rules")
@patch("dbt_governance.cli.load_rules")
def test_check_command_with_severity(mock_load_rules, mock_evaluate_rules, tmp_path: Path) -> None:
    """Test the `check` command with a severity filter."""
    runner = CliRunner()

    # Create a temporary rules.yml file
    rules_file = tmp_path / constants.DEFAULT_RULES_FILE_NAME
    rules_file.write_text(
        """
    - name: Owner Metadata
      severity: medium
    - name: Primary Key Test
      severity: high
    """
    )

    # Mock return values with real GovernanceRule objects
    mock_load_rules.return_value = [
        GovernanceRule(
            name="Owner Metadata",
            description="Ensure all models have an owner.",
            severity=Severity.MEDIUM,
            enabled=True,
        ),
        GovernanceRule(
            name="Primary Key Test",
            description="Ensure primary key tests exist.",
            severity=Severity.HIGH,
            enabled=True,
        ),
    ]

    # Create real GovernanceResult components
    details = [
        ValidationResult(
            rule_name="Primary Key Test",
            status=ValidationStatus.PASSED,
            dbt_project_path="path/to/dbt/project",
            resource_type="model",
            unique_id="model.my_project.dim_date",
            reason=None,
        )
    ]
    summary = GovernanceResultSummary(
        total_evaluations=1,
        total_passed=1,
        total_failed=0,
    )
    metadata = GovernanceResultMetadata(
        generated_at="2024-12-09T12:00:00Z",
        result_uuid="test-uuid",
        dbt_governance_version="0.1.0",
    )

    # Create a real GovernanceResult object
    results = GovernanceResult(summary=summary, metadata=metadata, results=details)
    mock_evaluate_rules.return_value = results

    # Invoke the CLI with severity filter
    result = runner.invoke(
        dbt_governance_cli,
        [
            "check",
            "--project-path",
            str(tmp_path),
            "--rules-file",
            str(rules_file),
            "--severity",
            "high",
        ],
    )

    # Assertions
    assert result.exit_code == 0, f"Unexpected output: {result.output}"
    assert "Governance Check Results:" in result.output
    assert "Passed: 1" in result.output
    assert "Failed: 0" in result.output
    # Verify the results.details contains only the high severity rule
    assert all(detail.rule_name == "Primary Key Test" for detail in results.results)
    assert not any(detail.rule_name == "Owner Metadata" for detail in results.results)

    # Verify mocks
    mock_load_rules.assert_called_once_with(str(rules_file))
    mock_evaluate_rules.assert_called_once()


@patch("dbt_governance.cli.load_rules")
def test_list_rules_command(mock_load_rules, tmp_path: Path) -> None:
    """Test the `list_rules` command."""
    runner = CliRunner()

    # Create a temporary rules.yml file
    rules_file = tmp_path / constants.DEFAULT_RULES_FILE_NAME
    rules_file.write_text(
        """
    - name: Owner Metadata
      severity: medium
      description: Ensure all models have an owner.
    - name: Primary Key Test
      severity: high
      description: Ensure primary key tests exist.
    """
    )

    # Mock return value with real GovernanceRule instances
    mock_load_rules.return_value = [
        GovernanceRule(
            name="Owner Metadata",
            description="Ensure all models have an owner.",
            severity=Severity.MEDIUM,
            enabled=True,
        ),
        GovernanceRule(
            name="Primary Key Test", description="Ensure primary key tests exist.", severity=Severity.HIGH, enabled=True
        ),
    ]

    # Invoke the CLI
    result = runner.invoke(dbt_governance_cli, ["list-rules", "--rules-file", str(rules_file)])

    # Assertions
    assert result.exit_code == 0, f"Unexpected output: {result.output}"
    assert "Owner Metadata" in result.output
    assert "Primary Key Test" in result.output
    assert "Ensure all models have an owner." in result.output
    assert "Ensure primary key tests exist." in result.output

    # Verify the mocked function was called
    mock_load_rules.assert_called_once_with(str(rules_file))


@patch("dbt_governance.cli.validate_config_structure")
def test_validate_config_valid(mock_validate_config_structure, tmp_path: Path) -> None:
    """Test the `validate_config` command with a valid configuration."""
    runner = CliRunner()

    # Create a temporary valid config file
    config_file = tmp_path / "config.yml"
    config_file.write_text(
        """
    dbt_cloud:
      api_token: "test_token"
    """
    )

    # Mock `validate_config_structure` to return no errors
    mock_validate_config_structure.return_value = []

    # Invoke the CLI
    result = runner.invoke(dbt_governance_cli, ["validate-config", "--config-file", str(config_file)])

    # Assertions
    assert result.exit_code == 0, f"Unexpected output: {result.output}"
    assert "Configuration file is valid!" in result.output
    assert mock_validate_config_structure.called


@patch("dbt_governance.cli.validate_config_structure")
def test_validate_config_yaml_error(mock_validate_config_structure, tmp_path: Path) -> None:
    """Test the `validate_config` command with a YAML syntax error."""
    runner = CliRunner()

    # Create a temporary invalid config file with YAML errors
    config_file = tmp_path / "config.yml"
    config_file.write_text("dbt_cloud:\n  api_token: test_token\n  invalid: [test]:")

    # Invoke the CLI
    result = runner.invoke(dbt_governance_cli, ["validate_config", "--config-file", str(config_file)])

    # Assertions
    assert result.exit_code == 0, f"Unexpected output: {result.output}"
    assert "YAML Parsing Error" in result.output
    assert not mock_validate_config_structure.called


@patch("dbt_governance.cli.validate_config_structure")
def test_validate_config_load_error(mock_validate_config_structure, tmp_path: Path) -> None:
    """Test the `validate_config` command with a file loading error."""
    runner = CliRunner()

    # Use a non-existent file
    config_file = tmp_path / "nonexistent_config.yml"

    # Invoke the CLI
    result = runner.invoke(dbt_governance_cli, ["validate_config", "--config-file", str(config_file)])

    # Assertions
    assert result.exit_code == 0, f"Unexpected output: {result.output}"
    assert "Failed to load configuration file" in result.output
    assert not mock_validate_config_structure.called


@patch("dbt_governance.cli.validate_config_structure")
def test_validate_config_with_validation_errors(mock_validate_config_structure, tmp_path: Path) -> None:
    """Test the `validate_config` command with validation errors."""
    runner = CliRunner()

    # Create a temporary config file
    config_file = tmp_path / "config.yml"
    config_file.write_text(
        """
    dbt_cloud:
      api_token: "test_token"
    """
    )

    # Mock `validate_config_structure` to return errors
    mock_validate_config_structure.return_value = ["Missing required field: dbt_project"]

    # Invoke the CLI
    result = runner.invoke(dbt_governance_cli, ["validate_config", "--config-file", str(config_file)])

    # Assertions
    assert result.exit_code == 0, f"Unexpected output: {result.output}"
    assert "Configuration validation failed with the following errors:" in result.output
    assert "- Missing required field: dbt_project" in result.output
    assert mock_validate_config_structure.called
