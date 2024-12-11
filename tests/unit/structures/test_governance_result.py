import pytest
from dbt_governance.structures.governance_result import (
    GovernanceResult,
    GovernanceResultMetadata,
    GovernanceResultSummary,
)
from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def test_governance_result_metadata() -> None:
    """Test GovernanceResultMetadata attributes and immutability."""
    metadata = GovernanceResultMetadata(
        generated_at="2024-12-09T12:00:00Z", result_uuid="abc123", dbt_governance_version="0.1.0"
    )
    assert metadata.generated_at == "2024-12-09T12:00:00Z"
    assert metadata.result_uuid == "abc123"
    assert metadata.dbt_governance_version == "0.1.0"

    with pytest.raises(AttributeError):
        metadata.generated_at = "2024-12-10T12:00:00Z"  # type: ignore


def test_governance_result_summary() -> None:
    """Test GovernanceResultSummary attributes."""
    summary = GovernanceResultSummary(total_evaluations=10, total_passed=8, total_failed=2)
    assert summary.total_evaluations == 10
    assert summary.total_passed == 8
    assert summary.total_failed == 2


def test_governance_result_summary_evaluations() -> None:
    """Ensure total_evaluations = total_passed + total_failed."""
    summary = GovernanceResultSummary(total_evaluations=10, total_passed=8, total_failed=2)
    assert summary.total_evaluations == summary.total_passed + summary.total_failed


def test_governance_result_to_dict() -> None:
    """Test GovernanceResult's to_dict method for correct serialization."""
    # Mock metadata
    metadata = GovernanceResultMetadata(
        generated_at="2024-12-09T12:00:00Z", result_uuid="abc123", dbt_governance_version="0.1.0"
    )

    # Mock summary
    summary = GovernanceResultSummary(total_evaluations=2, total_passed=1, total_failed=1)

    # Mock validation results
    validation_results_details = [
        ValidationResult(rule_name="Test Rule 1", status=ValidationStatus.PASSED, reason="Check passed"),
        ValidationResult(rule_name="Test Rule 2", status=ValidationStatus.FAILED, reason="Check failed"),
    ]

    # GovernanceResult
    governance_result = GovernanceResult(summary=summary, metadata=metadata, results=validation_results_details)

    expected_dict = {
        "summary": {"total_evaluations": 2, "total_passed": 1, "total_failed": 1},
        "metadata": {
            "generated_at": "2024-12-09T12:00:00Z",
            "result_uuid": "abc123",
            "dbt_governance_version": "0.1.0",
        },
        "results": [
            {"rule_name": "Test Rule 1", "status": "passed", "reason": "Check passed"},
            {"rule_name": "Test Rule 2", "status": "failed", "reason": "Check failed"},
        ],
    }
    assert governance_result.to_dict() == expected_dict
