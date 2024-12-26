from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from dbt_governance import constants


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
    default_projects: list[str] = Field(
        [], description="A list of default project names to use for dbt Cloud API interactions."
    )

    def __bool__(self):
        """Check if the DbtCloudConfig object has any values set."""
        return any(self.dict().values())

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
        project_path (str): Path to a single dbt project.
        project_paths (list[str]): List of dbt project paths.
        output_path (str): Path to the output file.
        global_rules_file (Optional[str]): Path to a global rules file.
        dbt_cloud (DbtCloudConfig): Configuration for dbt Cloud API interactions.

    """

    project_path: str = Field("", description="Path to a single dbt project.")
    project_paths: list[str] = Field([], description="List of dbt project paths.")
    output_path: str = Field(constants.DEFAULT_OUTPUT_FILE_NAME, description="Path to the output file.")
    global_rules_file: str = Field(constants.DEFAULT_RULES_FILE_NAME, description="Path to a global rules file.")
    dbt_cloud: Optional[DbtCloudConfig] = Field(None, description="Configuration for dbt Cloud API interactions.")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GovernanceConfig":
        return cls(
            project_path=data.get("project_path", ""),
            project_paths=data.get("project_paths", []),
            output_path=data.get("output_path", constants.DEFAULT_OUTPUT_FILE_NAME),
            global_rules_file=data.get("global_rules_file", constants.DEFAULT_RULES_FILE_NAME),
            dbt_cloud=DbtCloudConfig(
                api_token=data.get("dbt_cloud", {}).get("api_token", ""),
                organization_id=data.get("dbt_cloud", {}).get("organization_id", ""),
                default_projects=data.get("dbt_cloud", {}).get("default_projects", []),
            ),
        )

    def get_project_paths(self) -> list[str]:
        """Retrieve the list of project paths from the configuration.

        Returns:
            list: A list of project paths.

        Raises:
            ValueError: If no project paths are found in the configuration.
        """
        project_path_lists: list[str] = []
        if self.project_path:
            project_path_lists.append(self.project_path)
        elif self.project_paths:
            project_path_lists.extend(self.project_paths)
        else:
            raise ValueError("No project paths found in configuration.")

        return project_path_lists
