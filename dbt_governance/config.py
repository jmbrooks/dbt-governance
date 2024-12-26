import os
from typing import List, Optional

import yaml

import dbt_governance.constants as constants
from dbt_governance.logging_config import logger
from dbt_governance.structures.governance_config import GovernanceConfig


def load_global_config() -> GovernanceConfig:
    """Load the global configuration from the default config file path.

    Returns:
        dict: The global Governance configuration loaded from the file.
    """
    logger.debug(f"Loading global configuration from: {constants.DEFAULT_CONFIG_PATH}")

    if os.path.exists(constants.DEFAULT_CONFIG_PATH):
        with open(constants.DEFAULT_CONFIG_PATH, "r") as file:
            governance_config = GovernanceConfig.from_dict(yaml.safe_load(file))
    else:
        logger.warning(f"Global configuration file not found: {constants.DEFAULT_CONFIG_PATH}")
        governance_config = GovernanceConfig()  # Use default config values

    return governance_config


def load_config(
    project_path: Optional[str] = None, project_paths: Optional[List[str]] = None, rules_file: Optional[str] = None
) -> GovernanceConfig:
    """Merge configurations from global config, environment variables, and CLI options.

    Args:
        project_path (Optional[str]): Path to a single dbt project.
        project_paths (Optional[List[str]]): List of dbt project paths.
        rules_file (Optional[str]): Path to a custom rules file.

    Returns:
        The GovernanceConfig result after considering all config source options.
    """
    config = load_global_config()

    # Override with environment variables
    if os.getenv("DBT_PROJECT_PATHS"):
        env_project_paths = os.getenv("DBT_PROJECT_PATHS", "").split(",")
        config.project_paths = env_project_paths
    config.global_rules_file = os.getenv("DBT_GLOBAL_RULES_FILE", config.global_rules_file)
    config.dbt_cloud.api_token = os.getenv("DBT_CLOUD_API_TOKEN", config.dbt_cloud.api_token)

    # Override with CLI options
    if project_path:
        config.project_path = project_path
    if project_paths:
        config.project_paths = list(project_paths)
    if rules_file:
        config.global_rules_file = rules_file

    return config


def validate_config_structure(config: GovernanceConfig) -> List[str]:
    """Validate the structure of the configuration dictionary.

    Args:
        config (dict): The configuration dictionary to validate.

    Returns:
        list: A list of validation errors, empty if valid.
    """
    errors = []
    dbt_cloud_config = config.dbt_cloud

    # Validate required top-level keys
    if not config.project_path and not config.project_paths:
        errors.append("Missing required key: 'project_path' or 'project_paths'")

    # Validate nested dbt_cloud structure
    if dbt_cloud_config:
        if dbt_cloud_config.api_token == "":  # nosec: B105
            errors.append("Missing required key: 'dbt_cloud.api_token'")
        if dbt_cloud_config.organization_id == "":
            errors.append("Missing required key: 'dbt_cloud.organization_id'")

        # Confirm each project path is default_projects exists as a valid Path
        for project_path in dbt_cloud_config.default_projects:
            errors.append(f"dbt_cloud.default_projects: Invalid project path: {project_path}") \
                if not os.path.exists(project_path) else None

    return errors
