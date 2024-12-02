import os
import yaml
from typing import List, Dict, Optional

from dbt_governance.constants import DEFAULT_CONFIG_PATH
from dbt_governance.logging_config import logger

# Default configuration structure
DEFAULT_CONFIG = {
    "project_path": "",
    "project_paths": [],
    "global_rules_file": None,
    "dbt_cloud": {
        "api_token": None,
        "organization_id": None,
        "default_projects": []
    },
}


def load_global_config() -> Dict:
    """Load the global configuration from the default config file path.

    Returns:
        dict: The global configuration dictionary loaded from the file.
    """
    logger.info(f"Loading global configuration from: {DEFAULT_CONFIG_PATH}")
    config = DEFAULT_CONFIG.copy()

    if os.path.exists(DEFAULT_CONFIG_PATH):
        with open(DEFAULT_CONFIG_PATH, "r") as file:
            config.update(yaml.safe_load(file))

    return config


def load_config(
    project_path: Optional[str] = None,
    project_paths: Optional[List[str]] = None,
    rules_file: Optional[str] = None
) -> Dict:
    """Merge configurations from global config, environment variables, and CLI options.

    Args:
        project_path (Optional[str]): Path to a single dbt project.
        project_paths (Optional[List[str]]): List of dbt project paths.
        rules_file (Optional[str]): Path to a custom rules file.

    Returns:
        dict: The merged configuration dictionary.
    """
    config = load_global_config()

    # Override with environment variables
    if os.getenv("DBT_PROJECT_PATHS"):
        env_project_paths = os.getenv("DBT_PROJECT_PATHS", "").split(",")
        config["project_paths"] = env_project_paths
    config["global_rules_file"] = os.getenv("DBT_GLOBAL_RULES_FILE", config["global_rules_file"])
    config["dbt_cloud"]["api_token"] = os.getenv("DBT_CLOUD_API_TOKEN", config["dbt_cloud"]["api_token"])

    # Override with CLI options
    if project_path:
        config["project_path"] = project_path
    if project_paths:
        config["project_paths"] = list(project_paths)
    if rules_file:
        config["global_rules_file"] = rules_file

    return config


def validate_config_structure(config: Dict) -> List[str]:
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
            if key == "global_rules_file" and not (
                config[key] is None or isinstance(config[key], str)
            ):
                errors.append(f"Incorrect type for key '{key}': Expected None or str")
            # Default type check for other keys
            elif key != "global_rules_file" and not isinstance(config[key], type(DEFAULT_CONFIG[key])):
                errors.append(f"Incorrect type for key '{key}': Expected {type(DEFAULT_CONFIG[key]).__name__}")

    # Validate nested dbt_cloud structure
    if "dbt_cloud" in config:
        dbt_cloud = config["dbt_cloud"]
        if not isinstance(dbt_cloud, dict):
            errors.append(f"'dbt_cloud' must be a dictionary.")
        else:
            for sub_key, expected_type in DEFAULT_CONFIG["dbt_cloud"].items():
                if sub_key not in dbt_cloud:
                    errors.append(f"Missing key in 'dbt_cloud': {sub_key}")
                elif not isinstance(dbt_cloud[sub_key], type(expected_type)):
                    errors.append(f"Incorrect type for 'dbt_cloud.{sub_key}': Expected {type(expected_type).__name__}")

    # Validate project_paths as a list of strings
    if not all(isinstance(path, str) for path in config.get("project_paths", [])):
        errors.append("'project_paths' must be a list of strings.")

    return errors


def get_project_paths(config: Dict) -> List[str]:
    """Retrieve the list of project paths from the configuration.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        list: A list of project paths.
    """
    if config["project_path"]:
        return [config["project_path"]]
    return config["project_paths"]
