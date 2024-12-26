import pytest
from dbt_governance.structures.governance_rules_config import (
    PassRateAcceptanceThresholdsConfig,
    RuleEvaluationConfig,
    GovernanceRulesConfig,
)
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.severity import Severity


def test_pass_rate_acceptance_thresholds_from_dict() -> None:
    """Test the PassRateAcceptanceThresholdsConfig.from_dict method."""
    thresholds_data = {
        "overall": 0.95,
        "critical": 0.99,
        "high": 0.90,
        "medium": 0.85,
        "low": 0.80,
    }

    thresholds = PassRateAcceptanceThresholdsConfig.from_dict(thresholds_data)

    # Assertions
    assert thresholds.overall == 0.95
    assert thresholds.critical == 0.99
    assert thresholds.high == 0.90
    assert thresholds.medium == 0.85
    assert thresholds.low == 0.80

    # Test with missing fields
    partial_data = {"overall": 0.95}
    thresholds = PassRateAcceptanceThresholdsConfig.from_dict(partial_data)

    assert thresholds.overall == 0.95
    assert thresholds.critical is None
    assert thresholds.high is None
    assert thresholds.medium is None
    assert thresholds.low is None


def test_rule_evaluation_config_from_dict() -> None:
    """Test the RuleEvaluationConfig.from_dict method."""
    evaluation_config_data = {
        "default_severity": "medium",
        "pass_rate_acceptance_thresholds": {
            "overall": 0.95,
            "critical": 0.99,
            "high": 0.90,
            "medium": 0.85,
            "low": 0.80,
        },
    }

    config = RuleEvaluationConfig.from_dict(evaluation_config_data)

    # Assertions
    assert config.default_severity == "medium"
    assert config.pass_rate_acceptance_thresholds is not None
    assert config.pass_rate_acceptance_thresholds.overall == 0.95
    assert config.pass_rate_acceptance_thresholds.critical == 0.99

    # Test with missing thresholds
    minimal_data = {"default_severity": "low"}
    config = RuleEvaluationConfig.from_dict(minimal_data)

    assert config.default_severity == "low"
    assert not config.pass_rate_acceptance_thresholds.has_set_any_thresholds


def test_governance_rules_config_from_dict() -> None:
    """Test the GovernanceRulesConfig.from_dict method."""
    rules_config_data = {
        "rule_evaluation_config": {
            "default_severity": "high",
            "pass_rate_acceptance_thresholds": {
                "overall": 0.95,
                "critical": 0.99,
            },
        },
        "rules": [
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
                "description": "Ensure all models have an owner defined.",
                "severity": "medium",
                "enabled": True,
            },
        ],
    }

    config = GovernanceRulesConfig.from_dict(rules_config_data)

    # Assertions for rule evaluation config
    assert config.rule_evaluation_config.default_severity == "high"
    assert config.rule_evaluation_config.pass_rate_acceptance_thresholds.overall == 0.95
    assert config.rule_evaluation_config.pass_rate_acceptance_thresholds.critical == 0.99

    # Assertions for rules
    assert len(config.rules) == 2
    assert config.rules[0].name == "Primary Key Test"
    assert config.rules[0].severity == Severity.HIGH.value
    assert config.rules[1].name == "Owner Metadata"
    assert config.rules[1].severity == Severity.MEDIUM.value
