from dbt_governance.structures.severity import Severity

print(str(Severity.CRITICAL))


def test_severity_values() -> None:
    """Test that Severity Enum values are correct."""
    assert Severity.CRITICAL.value == "critical"
    assert Severity.HIGH.value == "high"
    assert Severity.MEDIUM.value == "medium"
    assert Severity.LOW.value == "low"


def test_severity_names() -> None:
    """Test that Severity Enum names are correct."""
    assert Severity.CRITICAL.name == "CRITICAL"
    assert Severity.HIGH.name == "HIGH"
    assert Severity.MEDIUM.name == "MEDIUM"
    assert Severity.LOW.name == "LOW"


def test_severity_string_representation() -> None:
    """Test the string representation of Severity Enum."""
    assert str(Severity.CRITICAL) == "critical"
    assert str(Severity.HIGH) == "high"
    assert str(Severity.MEDIUM) == "medium"
    assert str(Severity.LOW) == "low"


def test_severity_iteration() -> None:
    """Test that all Severity Enum members can be iterated over."""
    severities = list(Severity)
    assert severities == [
        Severity.CRITICAL,
        Severity.HIGH,
        Severity.MEDIUM,
        Severity.LOW,
    ]
