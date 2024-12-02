from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


def validate_primary_key_rule(rule, manifest: dict) -> list:
    """Validate the primary key test rule against dbt models.

    Args:
        rule (GovernanceRule): The rule to validate.
        manifest (dict): Parsed dbt manifest.json.

    Returns:
        list: Validation results for the rule.
    """
    results = []

    for model_name, model in manifest["nodes"].items():
        # Skip non-models
        if model["resource_type"] != "model":
            continue

        # Check for the primary key test
        has_primary_key_test = any(
            test["test_metadata"]["name"] == "unique"
            and rule.checks["required_columns"][0] in test.get("column_name", "")
            for test in model.get("tests", [])
        )

        if has_primary_key_test:
            results.append(
                ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.PASSED,
                    reason=None
                )
            )
        else:
            results.append(
                ValidationResult(
                    rule_name=rule.name,
                    status=ValidationStatus.FAILED,
                    reason=f"Model {model_name} is missing a unique test on its primary key."
                )
            )

    return results
