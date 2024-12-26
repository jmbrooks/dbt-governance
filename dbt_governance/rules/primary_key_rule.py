from dbt.contracts.graph.manifest import Manifest

from dbt_governance.logging_config import logger
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def validate_primary_key_rule(rule: GovernanceRule, manifest: Manifest, project_path: str) -> list[ValidationResult]:
    """Validate the primary key test rule against dbt models.

    Args:
        rule (GovernanceRule): The rule to validate.
        manifest (Manifest): The dbt Manifest object.
        project_path (str): The path to the dbt project directory.

    Returns:
        list[ValidationResult]: Validation results for the rule.
    """
    results: list[ValidationResult] = []

    for model_id, model in manifest.nodes.items():
        # Skip non-models
        if str(model.resource_type).lower() != "model":
            continue

        # Get the primary key column from the model's config
        primary_key = model.config.meta.get("primary_key")
        if not primary_key:
            results.append(
                ValidationResult(
                    rule_name=rule.name,
                    rule_severity=rule.severity,
                    dbt_project_path=project_path,
                    resource_type=model.resource_type,
                    unique_id=model.unique_id,
                    status=ValidationStatus.FAILED,
                    reason=f"Model {model_id} does not have a primary key defined in its config.",
                )
            )
            continue

        # Check for a unique test on the primary key column
        has_primary_key_test = False
        for test_id, test in manifest.nodes.items():
            if str(test.resource_type).lower() != "test":
                continue

            if test.depends_on.nodes == [model_id] and test.test_metadata.name == "primary_key":
                logger.debug(f"Model {model_id} identified to have primary key test: {test_id}")
                has_primary_key_test = True
                break

        if has_primary_key_test:
            results.append(
                ValidationResult(
                    rule_name=rule.name,
                    rule_severity=rule.severity,
                    dbt_project_path=project_path,
                    resource_type=model.resource_type,
                    unique_id=model.unique_id,
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
                    resource_type=model.resource_type,
                    unique_id=model.unique_id,
                    status=ValidationStatus.FAILED,
                    reason=f"Model {model_id}'s primary key column ({primary_key}) is missing a unique test.",
                )
            )

    return results
