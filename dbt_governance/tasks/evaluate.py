import os
from pathlib import Path
from typing import Any, Dict, List

import yaml

import dbt_governance.utils as utils
from dbt_governance.dbt_project import DbtProject
from dbt_governance.logging_config import logger
from dbt_governance.rules.has_meta_rules import has_meta_property
from dbt_governance.rules.has_tag_rules import has_tag
from dbt_governance.rules.model_owner_rule import model_owner_rule
from dbt_governance.rules.primary_key_rule import validate_primary_key_rule
from dbt_governance.structures.governance_result import (
    GovernanceResult,
    GovernanceResultMetadata,
    GovernanceResultSummary,
)
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.rule_evaluation import RuleEvaluation
from dbt_governance.structures.validation_result import ValidationStatus


def load_global_rules_config(rules_file: str) -> Dict[str, Any]:
    """Load the global configuration for governance rules from a YAML file.

    Args:
        rules_file (str): Path to the rules file.

    Returns:
        Dict: The global configuration dictionary.
    """
    if not rules_file or not os.path.exists(rules_file):
        logger.error(f"Rules file not found: {rules_file}")
        return {}

    try:
        with open(rules_file, "r") as f:
            data = yaml.safe_load(f)
        return data.get("global_config", {})
    except Exception as e:
        logger.error(f"Failed to load global configuration: {e}")
        return {}


def evaluate_task(
    rules: List[GovernanceRule],
    project_paths: List[str],
    check_uuid: str,
    dbt_governance_version: str,
) -> GovernanceResult:
    """CLI task action to evaluate governance rules against dbt project metadata.

    Args:
        rules (List[GovernanceRule]): List of governance rules.
        project_paths (List[str]): List of dbt project paths.
        check_uuid (str): UUID for the dbt-governance check run and result.
        dbt_governance_version (str): Version of the dbt-governance package (e.g. 0.6.1).

    Returns:
        GovernanceResult: Results of rule evaluations as ValidationResult instances and result metadata.

    Raises:
        FileNotFoundError: If the dbt project manifest file is not found.
    """
    all_results = []

    # Load project(s) manifest
    for project_path in project_paths:
        logger.debug(f"Loading dbt project at: {project_path}")
        # Load dbt manifest.json
        manifest_path = Path(project_path) / "target" / "manifest.json"
        logger.info(f"Loading dbt project manifest at: {manifest_path}")
        dbt_project = DbtProject(project_path=project_path)

        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found at path: {manifest_path}")

        manifest_data = dbt_project.load_manifest()

        # Iterate over rules and evaluate results against dbt project(s) artifacts
        for rule in rules:
            if not rule.enabled:
                logger.info(f"Skipping rule '{rule.name}' as it not marked as enabled in the rules config.")
                continue

            if rule.dbt_selection_clause:
                logger.debug(f"Applying dbt selection clause: {rule.dbt_selection_clause}")
                # selection_result = dbt_client.get_model_unique_ids_from_manifest()

            rule_evaluation = RuleEvaluation(
                rule=rule,
                dbt_project_path=project_path,
                dbt_project_version=dbt_project.dbt_version,
                dbt_project_manifest_generated_at=str(dbt_project.generated_at),
                dbt_selection_syntax=rule.dbt_selection_clause,
            )

            # Evaluation logic
            # 1. Evaluate 'exception' rules with uniquely specific checks
            if rule.name == "Owner Metadata":
                rule_evaluation.validation_results.extend(model_owner_rule(rule, manifest_data, project_path))
            if rule.name == "Primary Key Test":
                rule_evaluation.validation_results.extend(validate_primary_key_rule(rule, manifest_data, project_path))
            # 2. Evaluate generic pattern rules with a common function
            if rule.type == "has_meta":
                rule_evaluation.validation_results.extend(
                    has_meta_property(
                        rule,
                        manifest_data,
                        project_path,
                        rule.args.get("required_property"),
                        meta_property_allowed_values=rule.args.get("allowed_values"),
                    )
                )
            if rule.type == "has_tag":
                rule_evaluation.validation_results.extend(
                    has_tag(
                        rule,
                        manifest_data,
                        project_path,
                        rule.args.get("required_tag"),
                        select=rule.args.get("select"),
                        match_type=rule.args.get("match_type"),
                    )
                )

            all_results.extend(rule_evaluation.validation_results)
            logger.debug(f"Rule '{rule.name}' evaluated with status: {all_results[-1].status}")

    # Summarize results
    summary = GovernanceResultSummary(
        total_evaluations=len(all_results),
        total_passed=sum(1 for result in all_results if result.status == ValidationStatus.PASSED),
        total_failed=sum(1 for result in all_results if result.status == ValidationStatus.FAILED),
    )

    # Metadata
    metadata = GovernanceResultMetadata(
        generated_at=utils.get_utc_iso_timestamp(),
        result_uuid=check_uuid,
        dbt_governance_version=dbt_governance_version,
    )

    return GovernanceResult(summary=summary, metadata=metadata, results=all_results)
