from typing import List, Optional

from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def append_evaluation_result(
    is_passing_evaluation: bool,
    results: List[ValidationResult],
    rule: GovernanceRule,
    project_path: str,
    node: "NodeType",
    failed_evaluation_description: str,
    passed_evaluation_description: Optional[str] = None,
) -> None:
    """Append a ValidationResult object to the results list for any rule evaluation.

    Args:
        is_passing_evaluation (bool): Whether the evaluation passed or failed.
        results (list): The list of ValidationResult objects.
        rule (GovernanceRule): The rule to validate.
        project_path (str): The path to the dbt project directory.
        node (NodeType): The dbt node object.
        failed_evaluation_description (str): The reason for the failed evaluation.
        passed_evaluation_description (str): Optional reason for the passed evaluation (default is no pass description).
    """
    if is_passing_evaluation:
        results.append(
            ValidationResult(
                rule_name=rule.name,
                rule_severity=rule.severity,
                dbt_project_path=project_path,
                resource_type=node.resource_type,
                unique_id=node.unique_id,
                status=ValidationStatus.PASSED,
                reason=passed_evaluation_description,
            )
        )
    else:
        results.append(
            ValidationResult(
                rule_name=rule.name,
                rule_severity=rule.severity,
                dbt_project_path=project_path,
                resource_type=node.resource_type,
                unique_id=node.unique_id,
                status=ValidationStatus.FAILED,
                reason=failed_evaluation_description,
            )
        )
