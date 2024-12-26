import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from dbt.cli.main import dbtRunner, dbtRunnerResult
from dbt.contracts.graph.manifest import Manifest
from dbt.graph.graph import Graph
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, PrivateAttr
from typing_extensions import Annotated

import dbt_governance.utils as utils
from dbt_governance.logging_config import logger


class DbtProject(BaseModel):
    """A client for an individual dbt project, for interacting with dbt artifacts (such as the Manifest).

    Attributes:
        project_path (Path): Path to the dbt project root directory.
        _manifest (Manifest): The dbt Manifest object.
    """

    model_config = ConfigDict(strict=True)

    project_path: Annotated[Union[str, Path], AfterValidator(utils.validate_dbt_path)] = Field(
        ..., description="Path to the dbt project root directory."
    )
    _manifest: Optional[Manifest] = PrivateAttr(None)

    @property
    def manifest(self) -> Manifest:
        """Return the dbt Manifest object, loading the manifest if not already loaded."""
        return self._manifest if self._manifest else self.load_manifest()

    @property
    def generated_at(self) -> datetime:
        """Timestamp when the dbt project Manifest was generated.

        Returns:
            datetime: The timestamp when the Manifest was generated.
        """
        return self.manifest.metadata.generated_at

    @property
    def dbt_schema_version(self) -> str:
        """Get the dbt schema version used to generate the Manifest.

        Returns:
            str: The dbt schema version used to generate the Manifest.
        """
        return self.manifest.metadata.dbt_schema_version

    @property
    def dbt_version(self) -> str:
        """Get the dbt version used to generate the Manifest.

        Returns:
            str: The dbt version used to generate the Manifest.
        """
        return self.manifest.metadata.dbt_version

    @property
    def project_id(self) -> str:
        """The dbt project ID from the project Manifest.

        Returns:
            str: The dbt project ID.
        """
        return self.manifest.metadata.project_id

    @property
    def project_name(self) -> str:
        """The dbt project name from the project Manifest.

        Returns:
            str: The dbt project name.
        """
        return self.manifest.metadata.project_name

    def load_manifest(self) -> Manifest:
        """Load the dbt Manifest file and return it as a typed Manifest object.

        Returns:
            Manifest: The dbt Manifest object.

        Raises:
            FileNotFoundError: If the manifest.json file is not found.
            json.JSONDecodeError: If the file cannot be parsed.
        """
        manifest_path = self.project_path / "target" / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found at {manifest_path}")

        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)

        self._manifest = Manifest.from_dict(manifest_data)
        return self._manifest

    def get_model_nodes(self) -> dict[str, Any]:
        """Retrieve all model nodes from the Manifest.

        Returns:
            dict: A dictionary of model nodes keyed by their unique IDs.
        """
        return {k: v for k, v in self.manifest.nodes.items() if str(v.resource_type).lower() == "model"}

    def get_model_unique_ids_from_manifest(
        self,
        full_selection_clause: Optional[str] = None,
        select: Optional[str] = None,
        exclude: Optional[str] = None,
        force_parse: bool = False,
    ) -> tuple[bool, list[str]]:
        """
        Get model unique IDs matching dbt selection syntax using a compiled manifest.

        Args:
            full_selection_clause (str): The full dbt selection clause to use, essentially the entire selection clause
                (e.g. '--select tag:hourly --exclude my_project.marts.marketing').
            select (str): The dbt selection syntax for models to include (--select).
            exclude (str): The dbt selection syntax for models to exclude (--exclude).
            force_parse (bool, optional): Whether to force parsing the manifest. Defaults to False.

        Returns:
            list: A list of unique IDs for models matching the selection criteria.
        """
        if force_parse:
            logger.debug("Forcing re-parsing of the manifest based on `force_parse` setting")
            # use 'parse' command to load a Manifest
            res: dbtRunnerResult = dbtRunner().invoke(["parse"], project_dir=self.project_path)
            manifest: Manifest = res.result
            logger.debug(
                f"Finished forced re-parsing of the project, with updated manifest generation time: "
                f"{manifest.metadata.generated_at}"
            )

        # Create a Graph from the manifest
        graph = Graph(self.manifest)
        logger.debug(f"Graph created from manifest with {len(graph.nodes())} nodes")

        # reuse this manifest in subsequent commands to skip parsing
        dbt = dbtRunner(manifest=self.manifest)
        cli_args = ["ls"]
        if full_selection_clause:
            cli_args.extend([full_selection_clause])
        elif select or exclude:
            if select:
                cli_args.extend(["--select", select])
            if exclude:
                cli_args.extend(["--exclude", exclude])
        else:
            raise ValueError("No selection criteria provided.")

        invocation_output = dbt.invoke(cli_args, project_dir=self.project_path)

        # Use NodeSelector to apply selection
        # selector = NodeSelector(graph=graph, manifest=self.manifest)

        # selection_criteria = {"include": [select], "exclude": [exclude] if exclude else []}
        # selected_nodes = selector.get_nodes_from_criteria(selection_criteria)
        #
        # # Return list of unique IDs
        # return list(selected_nodes)

        return invocation_output.success, invocation_output.result
