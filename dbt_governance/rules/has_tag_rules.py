from typing import Optional

from dbt_governance.structures.validation_result import ValidationResult


def has_tag(
    evaluation_run_instance: "EvaluateRunner",
    rule,
    manifest,
    project_path: str,
    tag_name: str,
    column_check_type: Optional[str] = None,
    select: Optional[str] = None,
    match_type: Optional[str] = None,
) -> list[ValidationResult]:
    """Validate that all dbt models specify any required tags.

    Args:
        rule (GovernanceRule): The rule to validate.
        manifest (dbt.contracts.graph.manifest.Manifest): dbt manifest artifact object.
        project_path (str): The path to the dbt project directory.
        tag_name (str): The name of the required tag
        column_check_type (str): The type column check to rule, default None means column(s) are not being checked,
            and the rule evaluation is being run at the node (e.g. model, source, snapshot) level. Other values can be:
            1) 'all' - check all columns have the tag (uncommon)
            2) 'any' - check if any column (at least one) has the tag
            2) 'none' - check that no columns have the tag
        select (Optional[str]): A string to filter nodes to test.
        match_type (Optional[str]): The type of match to use for filtering nodes to test.

    Returns:
        list: A list of ValidationResult objects for the rule.
    """
    results: list[ValidationResult] = []
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
        is_passing_evaluation = tag_name in model_tags

        evaluation_run_instance.append_rule_evaluation_result(
            rule_evaluation_index=0,
            is_passing_evaluation=is_passing_evaluation,
            rule=rule,
            project_path=project_path,
            node_resource_type=node.resource_type,
            node_unique_id=node.unique_id,
            evaluation_description=f"Model {node_id} is missing required '{tag_name}' tag.",
        )

    return results
