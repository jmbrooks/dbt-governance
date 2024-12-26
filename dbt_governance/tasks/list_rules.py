from typing import List

from dbt_governance.config import load_config
from dbt_governance.initialize import load_rules
from dbt_governance.structures.governance_rule import GovernanceRule


def list_rules_task(project_path: str, project_paths: List[str], rules_file: str) -> List[GovernanceRule]:
    """CLI task action to return all configured and currently enabled Governance Rules via the project rules config.

    Args:
        project_path (Optional[str]): Path to a single dbt project.
        project_paths (Optional[List[str]]): List of dbt project paths.
        rules_file (Optional[str]): Path to a custom rules file.

    Returns:
        List of GovernanceRules currently enabled in the dbt-governance rules config.
    """
    config = load_config(project_path, project_paths, rules_file)
    governance_rules_config = load_rules(config.global_rules_file, include_not_enabled=False)
    return governance_rules_config.rules
