from unittest.mock import MagicMock, patch

import pytest

from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.severity import Severity
from dbt_governance.tasks.list_rules import list_rules_task


def test_list_rules_task_with_valid_config() -> None:
    """Test list_rules_task with a valid configuration and enabled rules."""
    mock_config = MagicMock()
    mock_config.global_rules_file = "mock_rules.yml"

    mock_rules = MagicMock()
    mock_rules.rules = [
        GovernanceRule(
            name="Primary Key Test",
            type="data",
            description="Ensure primary key tests are defined.",
            severity=Severity.HIGH,
            enabled=True,
            paths=["models/staging"],
        ),
        GovernanceRule(
            name="Owner Metadata",
            type="metadata",
            description="Ensure all models have an owner defined.",
            severity=Severity.MEDIUM,
            enabled=True,
            paths=None,
        ),
    ]

    with patch("dbt_governance.tasks.list_rules.load_config", return_value=mock_config) as mock_load_config:
        with patch("dbt_governance.tasks.list_rules.load_rules", return_value=mock_rules) as mock_load_rules:
            result = list_rules_task("project_path", ["project_paths"], "rules_file")

            # Assertions
            assert len(result) == 2
            assert result[0].name == "Primary Key Test"
            assert result[1].name == "Owner Metadata"
            mock_load_config.assert_called_once_with("project_path", ["project_paths"], "rules_file")
            mock_load_rules.assert_called_once_with("mock_rules.yml", include_not_enabled=False)


def test_list_rules_task_no_enabled_rules() -> None:
    """Test list_rules_task when no enabled rules are returned."""
    mock_config = MagicMock()
    mock_config.global_rules_file = "mock_rules.yml"

    mock_rules = MagicMock()
    mock_rules.rules = []  # No enabled rules

    with patch("dbt_governance.tasks.list_rules.load_config", return_value=mock_config) as mock_load_config:
        with patch("dbt_governance.tasks.list_rules.load_rules", return_value=mock_rules) as mock_load_rules:
            result = list_rules_task("project_path", ["project_paths"], "rules_file")

            # Assertions
            assert len(result) == 0
            mock_load_config.assert_called_once_with("project_path", ["project_paths"], "rules_file")
            mock_load_rules.assert_called_once_with("mock_rules.yml", include_not_enabled=False)


def test_list_rules_task_invalid_rules_file() -> None:
    """Test list_rules_task with an invalid or missing rules file."""
    mock_config = MagicMock()
    mock_config.global_rules_file = None  # Simulate a missing or invalid rules file

    with patch("dbt_governance.tasks.list_rules.load_config", return_value=mock_config) as mock_load_config:
        with patch(
            "dbt_governance.tasks.list_rules.load_rules", side_effect=FileNotFoundError("mocked file not found")
        ) as mock_load_rules:
            with pytest.raises(FileNotFoundError, match="mocked file not found"):
                list_rules_task("project_path", ["project_paths"], "rules_file")

            # Assertions
            mock_load_config.assert_called_once_with("project_path", ["project_paths"], "rules_file")
            mock_load_rules.assert_called_once_with(None, include_not_enabled=False)
