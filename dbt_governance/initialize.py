import os
from typing import Optional

import yaml

from dbt_governance.structures.governance_rules_config import GovernanceRulesConfig, RuleEvaluationConfig
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.rules.registry import RulesRegistry
from dbt_governance.logging_config import logger


def load_rules(rules_file: Optional[str], include_not_enabled: bool = False) -> GovernanceRulesConfig:
    """Load governance rules and thresholds from a YAML file.

    Args:
        rules_file (str): Path to the rules file.
        include_not_enabled (bool): Default False; if set True, return both enabled and not enabled rules.
    Returns:
        GovernanceRulesConfig: A dataclass containing the rules and evaluation configuration.

    Raises:
        FileNotFoundError: If the configured governance rules config file is not found.
        ValueError: If the rules file cannot be loaded for any reason other than not being found.
    """
    if not rules_file or not os.path.exists(rules_file):
        raise FileNotFoundError(f"Rules file not found: {rules_file}")

    try:
        with open(rules_file, "r") as f:
            yaml_data = yaml.safe_load(f) or {}

        rule_evaluation_config_data = yaml_data.get("rule_evaluation_config", {})
        rules_data = yaml_data.get("rules", [])

        rule_evaluation_config = RuleEvaluationConfig.from_dict(rule_evaluation_config_data)
        rules = []
        for rule_data in rules_data:
            try:
                rule = GovernanceRule.from_dict(rule_data)
                if not include_not_enabled and not rule.enabled:
                    logger.debug(f"Skipping rule '{rule.name}' as it not marked as enabled in the rules config.")
                    continue
                rules.append(rule)
                RulesRegistry.register_rule(rule)
            except TypeError as e:
                logger.error(f"Invalid rule format in rules file: {rule_data}. Error: {e}")

        return GovernanceRulesConfig(
            rule_evaluation_config=rule_evaluation_config,
            rules=rules,
        )
    except Exception as err:
        raise ValueError(f"Failed to load governance rules: {err}") from err
