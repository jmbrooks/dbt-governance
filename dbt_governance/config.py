import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict

import yaml

import dbt_governance.constants as constants
from dbt_governance.logging_config import logger

# Default configuration structure
DBT_CLOUD_CONFIG = TypedDict(
    "DBT_CLOUD_CONFIG",
    {
        "api_token": Optional[str],
        "organization_id": Optional[str],
        "default_projects": List[str],
    },
)


@dataclass
class DbtCloudConfig:
    """A dbt Cloud configuration, for authentication and API interactions if using dbt Cloud."""

    api_token: Optional[str]
    organization_id: Optional[str]
    default_projects: List[str]


@dataclass
class GovernanceConfig(dict):
    """A configuration object for the dbt-governance tool."""

    project_path: str
    project_paths: List[str]
    output_path: str
    global_rules_file: Optional[str]
    dbt_cloud: DbtCloudConfig

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GovernanceConfig":
        return cls(
            project_path=data.get("project_path", ""),
            project_paths=data.get("project_paths", []),
            output_path=data.get("output_path", constants.DEFAULT_OUTPUT_FILE_NAME),
            global_rules_file=data.get("global_rules_file", constants.DEFAULT_RULES_FILE_NAME),
            dbt_cloud=DbtCloudConfig(
                api_token=data.get("dbt_cloud", {}).get("api_token"),
                organization_id=data.get("dbt_cloud", {}).get("organization_id"),
                default_projects=data.get("dbt_cloud", {}).get("default_projects", []),
            ),
        )

    def get_project_paths(self) -> List[str]:
        """Retrieve the list of project paths from the configuration.

        Returns:
            list: A list of project paths.

        Raises:
            ValueError: If no project paths are found in the configuration.
        """
        project_path_lists: List[str] = []
        if self.project_path:
            project_path_lists.append(self.project_path)
        elif self.project_paths:
            project_path_lists.extend(self.project_paths)
        else:
            raise ValueError("No project paths found in configuration.")

        return project_path_lists


DEFAULT_CONFIG = GovernanceConfig(
    project_path="",
    project_paths=[],
    output_path=constants.DEFAULT_OUTPUT_FILE_NAME,
    global_rules_file=None,
    dbt_cloud=DbtCloudConfig(api_token=None, organization_id=None, default_projects=[]),
)


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
        governance_config = DEFAULT_CONFIG

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


def validate_config_structure(config: Dict[str, Any]) -> List[str]:
    """Validate the structure of the configuration dictionary.

    Args:
        config (dict): The configuration dictionary to validate.

    Returns:
        list: A list of validation errors, empty if valid.
    """
    errors = []

    # Validate required top-level keys
    required_keys = DEFAULT_CONFIG.keys()
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")
        else:
            # Special case for global_rules_file: allow None or str
            if key == "global_rules_file" and not (config[key] is None or isinstance(config[key], str)):
                errors.append(f"Incorrect type for key '{key}': Expected None or str")
            # Default type check for other keys
            elif key != "global_rules_file" and not isinstance(config[key], type(DEFAULT_CONFIG[key])):  # type: ignore
                errors.append(
                    f"Incorrect type for key '{key}': Expected {type(DEFAULT_CONFIG[key]).__name__}"  # type: ignore
                )

    # Validate nested dbt_cloud structure
    if "dbt_cloud" in config:
        dbt_cloud = config["dbt_cloud"]
        if not isinstance(dbt_cloud, dict):
            errors.append("'dbt_cloud' must be a dictionary.")
        else:
            for sub_key, expected_type in DEFAULT_CONFIG.get("dbt_cloud", {}).items():
                if sub_key not in dbt_cloud:
                    errors.append(f"Missing key in 'dbt_cloud': {sub_key}")
                elif not isinstance(dbt_cloud[sub_key], type(expected_type)):
                    errors.append(f"Incorrect type for 'dbt_cloud.{sub_key}': Expected {type(expected_type).__name__}")

    # Validate project_paths as a list of strings
    if not all(isinstance(path, str) for path in config.get("project_paths", [])):
        errors.append("'project_paths' must be a list of strings.")

    return errors
