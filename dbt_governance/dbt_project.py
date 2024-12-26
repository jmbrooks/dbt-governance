import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field

from dbt.cli.main import dbtRunner, dbtRunnerResult
from dbt.contracts.graph.manifest import Manifest
from dbt.graph.graph import Graph
from dbt.graph.selector import NodeSelector


class DbtProject(BaseModel):
    """A representation of a single dbt project, including the project path, name, dbt version, and Manifest object."""
    model_config = ConfigDict(frozen=True, strict=True)

    project_path: str = Field(..., description="The path to the dbt project directory.")
    project_name: str = Field(..., description="The name of the dbt project.")
    dbt_version: str = Field(..., description="The dbt version used to generate the Manifest.")
    manifest: Manifest = Field(..., description="The dbt Manifest object.")

    def __bool__(self):
        """Check if the DbtProject object has any values set."""
        return any(self.dict().values())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DbtProject":
        return cls(
            project_path=data.get("project_path", ""),
            project_name=data.get("project_name", ""),
            dbt_version=data.get("dbt_version", ""),
            manifest=Manifest.from_dict(data.get("manifest", {})),
        )


class DbtClient:
    """A client for interacting with dbt artifacts such as the Manifest."""

    def __init__(self, project_path: Union[Path, str]) -> None:
        """
        Initialize the DbtClient with the path to the dbt project.

        Args:
            project_path (Union[Path, str]): The root directory of the dbt project, as either a Path or string to the
                project path.
        """
        self.project_path = Path(project_path)
        self._manifest: Optional[Manifest] = None

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
    def dbt_version(self) -> str:
        """Get the dbt version used to generate the Manifest.

        Returns:
            str: The dbt version used to generate the Manifest.
        """
        return self.manifest.metadata.dbt_version

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

    def get_model_nodes(self) -> Dict[str, Any]:
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
    ) -> Tuple[bool, List[str]]:
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
            # use 'parse' command to load a Manifest
            res: dbtRunnerResult = dbtRunner().invoke(["parse"], project_dir=self.project_path)
            manifest: Manifest = res.result

        # Create a Graph from the manifest
        graph = Graph(self.manifest)

        # introspect manifest
        # e.g. assert every public model has a description
        for node in self.manifest.nodes.values():
            if node.resource_type == "model" and node.access == "public":
                assert node.description != "", f"{node.name} is missing a description"

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
