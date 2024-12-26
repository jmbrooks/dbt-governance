from typing import Optional, Union

from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def has_meta_property(
    rule,
    manifest,
    project_path: str,
    meta_property_name: str,
    meta_property_allowed_values: Optional[Union[list[str], str]] = None,
) -> list[ValidationResult]:
    """Validate that all dbt models specify any required meta properties (and property values, if needed).

    Args:
        rule (GovernanceRule): The rule to validate.
        manifest (dbt.contracts.graph.manifest.Manifest): dbt manifest artifact object.
        project_path (str): The path to the dbt project directory.
        meta_property_name (str): The name of the required meta property.
        meta_property_allowed_values (Union[List[str], str]): The value(s) of the meta property that allowed in order
            for the check to pass, if required for validation.

    Returns:
        list: A list of ValidationResult objects for the rule.
    """
    results: list[ValidationResult] = []

    for node_id, node in manifest.nodes.items():
        # Skip non-model nodes
        if node.resource_type != "model":
            continue

        # Check for the meta property, and optionally check for specific values
        model_meta_property = node.config.meta.get(meta_property_name)

        if meta_property_allowed_values:
            if isinstance(meta_property_allowed_values, str):
                meta_property_allowed_values = [meta_property_allowed_values]
            if model_meta_property in meta_property_allowed_values:
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
                        reason=f"Model {node_id} has an invalid '{meta_property_name}' meta property value: "
                        f"{model_meta_property}.",
                    )
                )
        if model_meta_property:
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
                    reason=f"Model {node_id} is missing required '{meta_property_name}' meta property.",
                )
            )

    return results
