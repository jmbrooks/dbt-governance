from dbt_governance.structures.severity import Severity
from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def test_validation_status_enum() -> None:
    """Test the ValidationStatus enum for correct string and repr behavior."""
    assert ValidationStatus.PASSED.value == "passed"
    assert ValidationStatus.FAILED.value == "failed"
    assert ValidationStatus.ERROR.value == "error"
    assert ValidationStatus.WARNING.value == "warning"

    assert repr(ValidationStatus.PASSED) == "The rule passed successfully."
    assert repr(ValidationStatus.FAILED) == "The rule failed validation."
    assert repr(ValidationStatus.ERROR) == "The rule could not be evaluated due to an issue."
    assert repr(ValidationStatus.WARNING) == "The rule raised a non-critical concern."


def test_validation_result_to_dict(dbt_project) -> None:
    """Test the to_dict method of ValidationResult for expected output."""
    project_path = dbt_project.project_path
    # Case with a reason provided
    result_with_reason = ValidationResult(
        rule_name="Example Rule",
        rule_severity=Severity.MEDIUM,
        dbt_project_path=project_path,
        resource_type="model",
        unique_id="model.my_project.dim_date",
        status=ValidationStatus.PASSED,
        reason="All checks passed",
    )
    expected_dict_with_reason = {
        "rule_name": "Example Rule",
        "rule_severity": "medium",
        "dbt_project_path": str(project_path),
        "resource_type": "model",
        "unique_id": "model.my_project.dim_date",
        "status": "passed",
        "reason": "All checks passed",
    }
    assert result_with_reason.to_dict() == expected_dict_with_reason

    # Case without a reason
    result_no_reason = ValidationResult(
        rule_name="Another Rule",
        rule_severity=Severity.MEDIUM,
        dbt_project_path=project_path,
        resource_type="model",
        unique_id="model.my_project.fct_orders",
        status=ValidationStatus.FAILED,
        reason=None,
    )
    expected_dict_no_reason = {
        "rule_name": "Another Rule",
        "rule_severity": "medium",
        "dbt_project_path": str(project_path),
        "resource_type": "model",
        "unique_id": "model.my_project.fct_orders",
        "status": "failed",
        "reason": None,
    }
    assert result_no_reason.to_dict() == expected_dict_no_reason


def test_validation_result_defaults(dbt_project) -> None:
    """Test the default behavior of ValidationResult for optional attributes."""
    result = ValidationResult(
        rule_name="Default Test Rule",
        status=ValidationStatus.WARNING,
        dbt_project_path=dbt_project.project_path,
        resource_type="model",
        unique_id="model.my_project.dim_date",
    )
    assert result.rule_name == "Default Test Rule"
    assert result.status == ValidationStatus.WARNING.value
    assert result.rule_severity == Severity.default_rule_severity()
    assert result.reason is None
