from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.severity import Severity


def test_governance_rule_defaults() -> None:
    """Test the default values of optional attributes in GovernanceRule."""
    rule = GovernanceRule(
        name="Test Rule",
        description="This is a test rule.",
        severity=Severity.HIGH,
    )
    assert rule.name == "Test Rule"
    assert rule.description == "This is a test rule."
    assert rule.severity == Severity.HIGH
    assert rule.enabled is True
    assert rule.paths is None
    assert rule.checks is None


def test_governance_rule_with_optional_values() -> None:
    """Test GovernanceRule with all attributes explicitly defined."""
    rule = GovernanceRule(
        name="Complex Rule",
        description="A rule with all attributes defined.",
        severity=Severity.LOW,
        enabled=False,
        paths=["models/staging", "models/warehouse"],
        checks={"primary_key": True, "owner_required": True},
    )
    assert rule.name == "Complex Rule"
    assert rule.description == "A rule with all attributes defined."
    assert rule.severity == Severity.LOW
    assert rule.enabled is False
    assert rule.paths == ["models/staging", "models/warehouse"]
    assert rule.checks == {"primary_key": True, "owner_required": True}


def test_governance_rule_mutable_attributes() -> None:
    """Ensure lists and dictionaries are independent for different instances."""
    rule1 = GovernanceRule(
        name="Rule 1",
        description="First rule",
        severity=Severity.CRITICAL,
        paths=["models/marts"],
        checks={"test_enabled": True},
    )
    rule2 = GovernanceRule(
        name="Rule 2",
        description="Second rule",
        severity=Severity.MEDIUM,
        paths=["models/raw"],
        checks={"test_enabled": False},
    )

    # Modify rule1 attributes
    rule1.paths.append("models/production")
    rule1.checks["new_check"] = True

    # Ensure rule2 remains unaffected
    assert rule2.paths == ["models/raw"]
    assert rule2.checks == {"test_enabled": False}
