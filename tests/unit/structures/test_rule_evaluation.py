import json
from pathlib import Path

from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.rule_evaluation import RuleEvaluation
from dbt_governance.structures.severity import Severity
from dbt_governance.structures.validation_result import ValidationResult


def test_rule_evaluation_initialization(mock_manifest_data: dict, tmp_path: Path) -> None:
    """Test the initialization of the RuleEvaluation class."""
    project_path = tmp_path / "dbt_project"
    dbt_project_file = project_path / "dbt_project.yml"
    manifest_path = project_path / "target" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    dbt_project_file.touch()

    # Write mock manifest data to the file
    with Path.open(manifest_path, "w") as f:
        json.dump(mock_manifest_data, f)

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
        dbt_project_path=project_path,
        resource_type="model",
        unique_id="model.sample_project.my_model",
    )

    rule_evaluation = RuleEvaluation(
        rule=rule,
        dbt_project_path=project_path,
        dbt_project_version="1.8.0",
        dbt_project_manifest_generated_at="2024-01-01T00:00:00Z",
        dbt_selection_syntax="staging+",
        evaluate_dbt_nodes=["model.sample_project.my_model"],
        validation_results=[validation_result],
    )

    # Assertions
    assert rule_evaluation.rule.name == "Primary Key Test"
    assert rule_evaluation.dbt_project_path == project_path
    assert rule_evaluation.dbt_project_version == "1.8.0"
    assert rule_evaluation.dbt_project_manifest_generated_at == "2024-01-01T00:00:00Z"
    assert rule_evaluation.dbt_selection_syntax == "staging+"
    assert rule_evaluation.evaluate_dbt_nodes == ["model.sample_project.my_model"]
    assert len(rule_evaluation.validation_results) == 1
    assert rule_evaluation.validation_results[0].rule_name == "Primary Key Test"
