from unittest.mock import patch

import pytest

from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.severity import Severity


def test_from_dict() -> None:
    """Test the GovernanceRule.from_dict method."""
    rule_data = {
        "name": "Primary Key Test",
        "type": "data",
        "description": "Ensure primary key tests are defined.",
        "severity": Severity.HIGH.value,
        "enabled": True,
        "paths": ["models/staging", "models/warehouse"],
        "args": {"select": "staging", "exclude": "archive"},
    }

    rule = GovernanceRule.from_dict(rule_data)

    # Assertions
    assert rule.name == "Primary Key Test"
    assert rule.type == "data"
    assert rule.description == "Ensure primary key tests are defined."
    assert rule.severity == Severity.HIGH.value
    assert rule.enabled is True
    assert rule.paths == ["models/staging", "models/warehouse"]
    assert rule.args == {"select": "staging", "exclude": "archive"}


def test_get_rule_by_name() -> None:
    """Test the GovernanceRule.get_rule_by_name method."""
    rules_data = [
        {
            "name": "Primary Key Test",
            "type": "data",
            "description": "Ensure primary key tests are defined.",
            "severity": "high",
            "enabled": True,
        },
        {
            "name": "Owner Metadata",
            "type": "metadata",
            "description": "Ensure models have an owner defined.",
            "severity": Severity.MEDIUM.value,
            "enabled": True,
        },
    ]

    rule = GovernanceRule.get_rule_by_name("Owner Metadata", rules_data)

    # Assertions
    assert rule.name == "Owner Metadata"
    assert rule.type == "metadata"
    assert rule.description == "Ensure models have an owner defined."
    assert rule.severity == Severity.MEDIUM.value
    assert rule.enabled is True

    # Test for non-existent rule
    with pytest.raises(ValueError, match="Rule not found in rules config data: Non-Existent Rule"):
        GovernanceRule.get_rule_by_name("Non-Existent Rule", rules_data)


@patch("dbt_governance.structures.governance_rule.utils.assemble_dbt_selection_clause")
def test_dbt_selection_clause(mock_assemble_dbt_selection_clause) -> None:
    """Test the dbt_selection_clause property."""
    mock_assemble_dbt_selection_clause.return_value = "staging+ exclude:archive"

    rule_data = {
        "name": "Primary Key Test",
        "type": "data",
        "description": "Ensure primary key tests are defined.",
        "severity": "high",
        "enabled": True,
        "args": {"select": "staging", "exclude": "archive"},
    }
    rule = GovernanceRule.from_dict(rule_data)

    # Assertions
    assert rule.dbt_selection_clause == "staging+ exclude:archive"
    mock_assemble_dbt_selection_clause.assert_called_once_with("staging", "archive")


# Test the dbt_selection_clause property with no args
def test_dbt_selection_clause_no_args() -> None:
    """Test the dbt_selection_clause property with no args."""
    rule_data = {
        "name": "Primary Key Test",
        "type": "data",
        "description": "Ensure primary key tests are defined.",
        "severity": "high",
        "enabled": True,
    }
    rule = GovernanceRule.from_dict(rule_data)

    # Assertions
    assert rule.dbt_selection_clause == ""
