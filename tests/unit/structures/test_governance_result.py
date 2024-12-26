import pytest
from pydantic import ValidationError

from dbt_governance.structures.governance_result import (
    GovernanceResult,
    GovernanceResultMetadata,
    GovernanceResultSummary,
)
from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def test_governance_result_metadata() -> None:
    """Test GovernanceResultMetadata attributes and validation."""
    # Valid data
    metadata = GovernanceResultMetadata(
        generated_at="2024-12-09T12:00:00Z", result_uuid="abc123", dbt_governance_version="0.1.0"
    )
    assert metadata.generated_at == "2024-12-09T12:00:00Z"
    assert metadata.result_uuid == "abc123"
    assert metadata.dbt_governance_version == "0.1.0"

    # Invalid data (e.g., missing required field)
    with pytest.raises(ValidationError, match="Field required"):
        GovernanceResultMetadata(result_uuid="abc123", dbt_governance_version="0.1.0")  # Missing generated_at


def test_governance_result_summary() -> None:
    """Test GovernanceResultSummary attributes."""
    summary = GovernanceResultSummary(total_evaluations=10, total_passed=8, total_failed=2)
    assert summary.total_evaluations == 10
    assert summary.total_passed == 8
    assert summary.total_failed == 2


def test_governance_result_summary_pass_rate() -> None:
    """Test GovernanceResultSummary's pass_rate property."""
    summary = GovernanceResultSummary(total_evaluations=1000, total_passed=1000, total_failed=0)
    assert summary.pass_rate == 1.0

    summary = GovernanceResultSummary(total_evaluations=10, total_passed=8, total_failed=2)
    assert summary.pass_rate == 0.8

    summary = GovernanceResultSummary(total_evaluations=0, total_passed=0, total_failed=0)
    assert summary.pass_rate == 0.0


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
    project_path = "path/to/dbt/project"
    validation_results_details = [
        ValidationResult(
            rule_name="Test Rule 1",
            status=ValidationStatus.PASSED,
            dbt_project_path=project_path,
            resource_type="model",
            unique_id="model.my_project.dim_date",
            reason="Check passed",
        ),
        ValidationResult(
            rule_name="Test Rule 2",
            status=ValidationStatus.FAILED,
            dbt_project_path=project_path,
            resource_type="model",
            unique_id="model.my_project.fct_orders",
            reason="Check failed",
        ),
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
            {
                "rule_name": "Test Rule 1",
                "rule_severity": "medium",
                "status": "passed",
                "dbt_project_path": project_path,
                "resource_type": "model",
                "unique_id": "model.my_project.dim_date",
                "reason": "Check passed",
            },
            {
                "rule_name": "Test Rule 2",
                "rule_severity": "medium",
                "status": "failed",
                "dbt_project_path": project_path,
                "resource_type": "model",
                "unique_id": "model.my_project.fct_orders",
                "reason": "Check failed",
            },
        ],
    }
    assert governance_result.to_dict() == expected_dict
