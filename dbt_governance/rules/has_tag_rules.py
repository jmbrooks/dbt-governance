from typing import List, Optional, Union

from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def has_tag(
    rule,
    manifest,
    project_path: str,
    tag_name: str,
    select: Optional[str] = None,
    match_type: Optional[str] = None,
) -> List[ValidationResult]:
    """Validate that all dbt models specify any required tags.

    Args:
        rule (GovernanceRule): The rule to validate.
        manifest (dbt.contracts.graph.manifest.Manifest): dbt manifest artifact object.
        project_path (str): The path to the dbt project directory.
        tag_name (str): The name of the required tag
        select (Optional[str]): A string to filter nodes to test.
        match_type (Optional[str]): The type of match to use for filtering nodes to test.

    Returns:
        list: A list of ValidationResult objects for the rule.
    """
    results: List[ValidationResult] = []
    match_orientation = "match"

    for node_id, node in manifest.nodes.items():
        # Skip non-model nodes
        if node.resource_type != "model":
            continue

        # If select and match_type are provided, filter nodes to test
        if select and not match_type:
            raise ValueError("Both select and match_type must be provided in order to filter nodes to test.")
        if match_type.startswith("not "):
            match_orientation = "mismatch"

        if select and match_type:
            if match_type == "startswith":
                if match_orientation == "match":
                    if not node.name.startswith(select):
                        continue
                else:
                    if node.name.startswith(select):
                        continue
            elif match_type == "endswith":
                if match_orientation == "match":
                    if not node.name.endswith(select):
                        continue
                else:
                    if node.name.endswith(select):
                        continue
            elif match_type == "contains":
                if match_orientation == "match":
                    if select not in node.name:
                        continue
                else:
                    if select in node.name:
                        continue
            else:
                raise ValueError(f"Invalid match_type: '{match_type}' for rule: '{rule.name}'.")

        # Check for the meta tag
        model_tags = node.config.tags if node.config.tags else node.tags

        if tag_name in model_tags:
            results.append(
                ValidationResult(
                    rule_name=rule.name,
                    rule_severity=rule.severity,
                    dbt_project_path=project_path,
                    resource_type=node.resource_type,
                    unique_id=node.unique_id,
                    status=ValidationStatus.PASSED,
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
                    reason=f"Model {node_id} is missing required '{tag_name}' tag.",
                )
            )

    return results
