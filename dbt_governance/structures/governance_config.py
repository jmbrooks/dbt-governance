import os
from pathlib import Path
from typing import Any, Optional, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field

from dbt_governance import constants
from dbt_governance.logging_config import logger


class DbtCloudConfig(BaseModel):
    """A dbt Cloud configuration, for authentication and API interactions if using dbt Cloud.

    Attributes:
        api_token (Optional[str]): The dbt Cloud API token.
        organization_id (Optional[str]): The dbt Cloud organization ID.
        default_projects (list[str]): A list of default project names to use for dbt Cloud API interactions.

    """

    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    api_token: str = Field(..., description="The dbt Cloud API token.")
    organization_id: str = Field(..., description="The dbt Cloud organization ID.")
    default_projects: Optional[list[str]] = Field(
        ..., description="A list of default project names to use for dbt Cloud API interactions."
    )

    def __post_init__(self):
        """Post initialization steps for dbt cloud configuration."""
        if self.default_projects is None:
            self.default_projects = []

    def __bool__(self):
        """Check if the DbtCloudConfig object has any values set."""
        return any(self.model_dump().values())

    @classmethod
    def from_governance_config(cls, governance_config: "GovernanceConfig") -> "DbtCloudConfig":
        """Create a DbtCloudConfig object from a GovernanceConfig object."""
        return cls(
            api_token=governance_config.dbt_cloud.api_token,
            organization_id=governance_config.dbt_cloud.organization_id,
            default_projects=governance_config.dbt_cloud.default_projects,
        )


class GovernanceConfig(BaseModel):
    """A configuration object for the dbt-governance tool.

    Attributes:
        project_path (Optional[str]): Path to a single dbt project, must specify either this or project_paths.
        project_paths (Optional[list[str]]): List of dbt project paths, must specify either this or project_path.
        output_path (str): Path to the output file.
        global_rules_file (Optional[str]): Path to a global rules file.
        dbt_cloud (DbtCloudConfig): Configuration for dbt Cloud API interactions.
    """

    project_path: Optional[Path] = Field(None, description="Path to a single dbt project.")
    project_paths: Optional[list[Path]] = Field(None, description="List of dbt project paths.")
    output_path: str = Field(constants.DEFAULT_OUTPUT_FILE_NAME, description="Path to the output file.")
    global_rules_file: str = Field(constants.DEFAULT_RULES_FILE_NAME, description="Path to a global rules file.")
    dbt_cloud: Optional[DbtCloudConfig] = Field(None, description="Configuration for dbt Cloud API interactions.")

    def __post_init__(self):
        """Post initialization steps for GovernanceConfig."""
        if self.project_paths is None:
            self.project_paths = []

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GovernanceConfig":
        return cls(
            project_path=Path(data.get("project_path", "")),
            project_paths=data.get("project_paths", []),
            output_path=data.get("output_path", constants.DEFAULT_OUTPUT_FILE_NAME),
            global_rules_file=data.get("global_rules_file", constants.DEFAULT_RULES_FILE_NAME),
            dbt_cloud=DbtCloudConfig(
                api_token=data.get("dbt_cloud", {}).get("api_token", ""),
                organization_id=data.get("dbt_cloud", {}).get("organization_id", ""),
                default_projects=data.get("dbt_cloud", {}).get("default_projects", []),
            ),
        )

    def get_project_paths(self) -> list[Path]:
        """Retrieve the list of project paths from the configuration.

        Returns:
            list: A list of project paths.

        Raises:
            ValueError: If no project paths are found in the configuration.
        """
        project_path_lists: list[Path] = []
        if self.project_path:
            project_path_lists.append(self.project_path)
        elif self.project_paths:
            project_path_lists.extend(self.project_paths)
        else:
            raise ValueError("No project paths found in configuration.")

        return project_path_lists

    @classmethod
    def load_config(
        cls,
        project_path: Optional[Union[str, Path]] = None,
        project_paths: Optional[Union[list[str], list[Path]]] = None,
        rules_file: Optional[str] = None,
    ) -> "GovernanceConfig":
        """Merge configurations from global config, environment variables, and CLI options.

        Args:
            project_path (Optional[Union[str, Path]]): Path to a single dbt project.
            project_paths (Optional[Union[list[str], list[Path]]]): List of dbt project paths.
            rules_file (Optional[str]): Path to a custom rules file.

        Returns:
            The GovernanceConfig result after considering all config source options.
        """
        # First, load any configs from the global config file, if set
        logger.debug(f"Loading global configuration from: {constants.DEFAULT_CONFIG_PATH}")
        governance_config = GovernanceConfig()

        if Path.exists(constants.DEFAULT_CONFIG_PATH):
            with Path.open(constants.DEFAULT_CONFIG_PATH, mode="r") as file:
                governance_config = GovernanceConfig.from_dict(yaml.safe_load(file))
        else:
            logger.warning(f"Global configuration file not found: {constants.DEFAULT_CONFIG_PATH}")

        # Override with environment variables, if specified
        if os.getenv("DBT_PROJECT_PATHS"):
            env_project_paths = os.getenv("DBT_PROJECT_PATHS", "").split(",")
            governance_config.project_paths = env_project_paths
        if os.getenv("DBT_GLOBAL_RULES_FILE"):
            governance_config.global_rules_file = os.getenv("DBT_GLOBAL_RULES_FILE")
        if os.getenv("DBT_CLOUD_API_TOKEN"):
            governance_config.dbt_cloud.api_token = os.getenv(
                "DBT_CLOUD_API_TOKEN", governance_config.dbt_cloud.api_token
            )

        # Finally, override with CLI options, if specified
        governance_config.project_paths = (
            [Path(project_path) for project_path in project_paths] if project_paths else [project_path]
        )

        if rules_file:
            governance_config.global_rules_file = rules_file

        return cls(
            project_path=governance_config.project_path,
            project_paths=governance_config.project_paths,
            output_path=governance_config.output_path,
            global_rules_file=governance_config.global_rules_file,
            dbt_cloud=governance_config.dbt_cloud,
        )

    def validate_config_structure(self) -> list[str]:
        """Validate the structure of the configuration dictionary.

        Returns:
            list: A list of validation errors, empty if valid.
        """
        errors = []
        dbt_cloud_config = self.dbt_cloud

        # Validate required top-level keys
        if not self.project_path and not self.project_paths:
            errors.append("Missing required key: 'project_path' or 'project_paths'")

        # Validate nested dbt_cloud structure
        if dbt_cloud_config:
            if dbt_cloud_config.api_token == "":  # nosec: B105
                errors.append("Missing required key: 'dbt_cloud.api_token'")
            if dbt_cloud_config.organization_id == "":
                errors.append("Missing required key: 'dbt_cloud.organization_id'")

            # Confirm each project path is default_projects exists as a valid Path
            for project_path in dbt_cloud_config.default_projects:
                errors.append(f"dbt_cloud.default_projects: Invalid project path: {project_path}") if not Path.exists(
                    Path(project_path)
                ) else None

        return errors
