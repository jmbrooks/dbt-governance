from dbt_governance.structures.rule_evaluation import RuleEvaluation
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.validation_result import ValidationResult
from dbt_governance.structures.severity import Severity


def test_rule_evaluation_initialization() -> None:
    """Test the initialization of the RuleEvaluation class."""
    rule = GovernanceRule(
        name="Primary Key Test",
        type="data",
        description="Ensure primary key tests are defined.",
        severity=Severity.HIGH,
        enabled=True,
        args={"select": "staging"},
        paths=["models/staging"],
    )

    validation_result = ValidationResult(
        rule_name="Primary Key Test",
        status="passed",
        reason=None,
        dbt_project_path="/path/to/dbt_project",
        resource_type="model",
        unique_id="model.sample_project.my_model",
    )

    rule_evaluation = RuleEvaluation(
        rule=rule,
        dbt_project_path="/path/to/dbt_project",
        dbt_project_version="1.8.0",
        dbt_project_manifest_generated_at="2024-01-01T00:00:00Z",
        dbt_selection_syntax="staging+",
        evaluate_dbt_nodes=["model.sample_project.my_model"],
        validation_results=[validation_result],
    )

    # Assertions
    assert rule_evaluation.rule.name == "Primary Key Test"
    assert rule_evaluation.dbt_project_path == "/path/to/dbt_project"
    assert rule_evaluation.dbt_project_version == "1.8.0"
    assert rule_evaluation.dbt_project_manifest_generated_at == "2024-01-01T00:00:00Z"
    assert rule_evaluation.dbt_selection_syntax == "staging+"
    assert rule_evaluation.evaluate_dbt_nodes == ["model.sample_project.my_model"]
    assert len(rule_evaluation.validation_results) == 1
    assert rule_evaluation.validation_results[0].rule_name == "Primary Key Test"


def test_rule_evaluation_to_dict() -> None:
    """Test the to_dict method of the RuleEvaluation class."""
    rule = GovernanceRule(
        name="Owner Metadata",
        type="metadata",
        description="Ensure all models have an owner defined.",
        severity=Severity.MEDIUM,
        enabled=True,
        args=None,
        paths=None,
    )

    rule_evaluation = RuleEvaluation(
        rule=rule,
        dbt_project_path="/path/to/dbt_project",
        dbt_project_version="1.9.0",
        dbt_project_manifest_generated_at="2024-01-02T00:00:00Z",
        dbt_selection_syntax=None,
        evaluate_dbt_nodes=[],
        validation_results=[],
    )

    result_dict = rule_evaluation.to_dict()

    # Assertions
    assert isinstance(result_dict, dict)
    assert result_dict["rule"]["name"] == "Owner Metadata"
    assert result_dict["dbt_project_path"] == "/path/to/dbt_project"
    assert result_dict["dbt_project_version"] == "1.9.0"
    assert result_dict["dbt_project_manifest_generated_at"] == "2024-01-02T00:00:00Z"
    assert result_dict["dbt_selection_syntax"] is None
    assert result_dict["evaluate_dbt_nodes"] == []
    assert result_dict["validation_results"] == []
