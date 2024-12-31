from pathlib import Path

import yaml

from dbt_governance.config import validate_config_structure
from dbt_governance.logging_config import logger
from dbt_governance.structures.governance_config import GovernanceConfig


def validate_config_task(config_file: str) -> tuple[bool, str]:
    """CLI task to validate the dbt-governance configuration file at the given path.

    Args:
        config_file (str): The path to the configuration file to validate.

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating if the configuration is valid and a message
        describing the result of the validation.
    """
    is_valid_config = True
    validity_message = ""

    try:
        with Path.open(Path(config_file), mode="r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as err:
        is_valid_config = False
        validity_message = f"Yaml parsing error: {err}"
    except Exception as err:
        is_valid_config = False
        validity_message = f"Failed to load configuration file: {err}"

    if is_valid_config:  # If config is still valid, validate the structure
        # Create GovernanceConfig object from yaml data
        dbt_governance_config = GovernanceConfig.from_dict(config)
        errors = validate_config_structure(dbt_governance_config)

        if errors:
            for error in errors:
                validity_message += f"- {error}"

        # Log the loaded configuration (sensitive keys redacted)
        redacted_config = dbt_governance_config.model_copy()
        if redacted_config and redacted_config.dbt_cloud.api_token:
            redacted_config.dbt_cloud.api_token = "REDACTED"  # nosec B105 (no hardcode issue, false flag)
        logger.debug(f"Loaded Configuration: {redacted_config}")

        if not validity_message:  # If no errors, set to success validity message
            validity_message = "Configuration file is valid!"

    return is_valid_config, validity_message
