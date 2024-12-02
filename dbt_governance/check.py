import os
import json
import yaml
from pathlib import Path
from typing import List

from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus
from dbt_governance.logging_config import logger
from dbt_governance.rules.primary_key_rule import validate_primary_key_rule


def load_rules(rules_file: str) -> list:
    """Load governance rules from a YAML file.

    Args:
        rules_file (str): Path to the rules file.

    Returns:
        list: A list of governance rules.
    """
    if not rules_file or not os.path.exists(rules_file):
        logger.error("Rules file not found: %s", rules_file)
        return []

    try:
        with open(rules_file, "r") as f:
            rules = yaml.safe_load(f)
        return rules or []
    except Exception as e:
        logger.error("Failed to load rules file: %s", e)
        return []


def evaluate_rules(rules: list, project_paths: List[str]) -> List[ValidationResult]:
    """Evaluate governance rules against dbt project metadata.

    Args:
        rules (list): List of governance rules.
        project_paths (list): List of dbt project paths.

    Returns:
        list: Results of rule evaluations as ValidationResult instances.
    """
    results = []

    # Load project(s) manifest
    for project_path in project_paths:
        # Load dbt manifest.json
        manifest_path = Path(project_path) / "target" / "manifest.json"
        if not manifest_path.exists():
            results.append(
                ValidationResult(
                    rule_name="Load Manifest",
                    status=ValidationStatus.ERROR,
                    reason=f"Manifest not found at {manifest_path}."
                )
            )
            continue

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

    for rule in rules:
        # Simulated evaluation logic
        if rule.name == "Primary Key Test":
            results.extend(validate_primary_key_rule(rule, manifest))
        # elif rule.name == "Owner Metadata":
        #     result = ValidationResult(
        #         rule_name=rule.name,
        #         status=ValidationStatus.FAILED,
        #         reason="The 'owner' meta property is missing."
        #     )
        # else:
        #     result = ValidationResult(
        #         rule_name=rule.name,
        #         status=ValidationStatus.WARNING,
        #         reason="This rule flagged a concern but is not critical."
        #     )

        # Log detailed result
        # logger.info("Rule '%s' evaluated with status: %s", rule.name, str(result.status))
        # if result.reason:
        #     logger.info("Reason: %s", result.reason)
        # results.append(result)

    return results
