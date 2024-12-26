from typing import List, Optional

from dbt_governance.constants import DEFAULT_OWNER_META_PROPERTY_NAME
from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def model_owner_rule(
    rule,
    manifest,
    project_path: str,
    owner_meta_property_name: Optional[str] = None,
) -> List[ValidationResult]:
    """Validate that all dbt models specify a meta property for model ownership (default 'owner').

    Args:
        rule (GovernanceRule): The rule to validate.
        manifest (dbt.contracts.graph.manifest.Manifest): dbt manifest artifact object.
        project_path (str): The path to the dbt project directory.
        owner_meta_property_name (str): The name of the owner meta property, default 'owner'.

    Returns:
        list: A list of ValidationResult objects for the rule.
    """
    results = []

    if not owner_meta_property_name:
        owner_meta_property_name = DEFAULT_OWNER_META_PROPERTY_NAME

    for node_id, node in manifest.nodes.items():
        # Skip non-model nodes
        if node.resource_type != "model":
            continue

        # Check for the 'owner' meta property
        owner = node.config.meta.get(owner_meta_property_name)
        if owner:
            results.append(
                ValidationResult(
                    rule_name=rule.name,
                    rule_severity=rule.severity,
                    dbt_project_path=project_path,
                    resource_type=node.resource_type,
                    unique_id=node.unique_id,
                    status=ValidationStatus.PASSED,
                    reason=None,
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
                    reason=f"Model {node_id} is missing '{owner_meta_property_name}' meta property for "
                    f"model ownership.",
                )
            )

    return results
