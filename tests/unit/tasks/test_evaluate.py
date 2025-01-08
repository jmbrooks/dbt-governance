from pathlib import Path
from unittest.mock import MagicMock

import pytest

from dbt_governance.structures.evaluate_runner import EvaluateRunner
from dbt_governance.structures.governance_result import GovernanceResult
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.severity import Severity
from dbt_governance.tasks.evaluate import evaluate_task


def test_evaluate_task_valid_rules(dbt_project, tmp_path: Path) -> None:
    """Test evaluate_task with valid rules and a valid dbt project."""
    # Mock EvaluateRunner
    evaluate_run_instance = MagicMock(spec=EvaluateRunner)

    # Mock manifest.json path
    manifest_path = tmp_path / "dbt_project/target/manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("{}")  # Mock manifest content

    # Mock rules
    rules = [
        GovernanceRule(
            name="Primary Key Test",
            type="data",
            description="Ensure primary key tests are defined.",
            severity=Severity.HIGH,
            enabled=True,
        ),
        GovernanceRule(
            name="Owner Metadata",
            type="metadata",
            description="Ensure all models have an owner defined.",
            severity=Severity.MEDIUM,
            enabled=True,
        ),
    ]

    # Call the function
    result = evaluate_task(
        evaluate_run_instance=evaluate_run_instance,
        rules=rules,
        project_paths=[tmp_path / "dbt_project"],
        check_uuid="123e4567-e89b-12d3-a456-426614174000",
        dbt_governance_version="0.1.0",
    )

    # Assertions
    assert isinstance(result, GovernanceResult)
    assert result.metadata.generated_at is not None
    assert result.metadata.dbt_governance_version == "0.1.0"
    assert result.metadata.result_uuid == "123e4567-e89b-12d3-a456-426614174000"
    assert result.summary.total_evaluations == 0  # No validations executed


def test_evaluate_task_no_enabled_rules(dbt_project, tmp_path) -> None:
    """Test evaluate_task with no enabled rules."""
    # Mock EvaluateRunner
    evaluate_run_instance = MagicMock(spec=EvaluateRunner)

    # Mock manifest.json path
    manifest_path = tmp_path / "dbt_project/target/manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("{}")  # Mock manifest content

    # Mock rules
    rules = [
        GovernanceRule(
            name="Disabled Rule",
            type="data",
            description="A rule that is disabled.",
            severity=Severity.LOW,
            enabled=False,
        )
    ]

    # Call the function
    result = evaluate_task(
        evaluate_run_instance=evaluate_run_instance,
        rules=rules,
        project_paths=[dbt_project.project_path],
        check_uuid="123e4567-e89b-12d3-a456-426614174000",
        dbt_governance_version="0.1.0",
    )

    # Assertions
    assert result.summary.total_evaluations == 0
    assert len(result.results) == 0
