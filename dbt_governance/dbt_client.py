import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from dbt.contracts.graph.manifest import Manifest


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

    def get_dbt_version(self) -> str:
        """Get the dbt version used to generate the Manifest.

        Returns:
            str: The dbt version.
        """
        return self.manifest.metadata.dbt_version

    def get_model_nodes(self) -> Dict[str, Any]:
        """Retrieve all model nodes from the Manifest.

        Returns:
            dict: A dictionary of model nodes keyed by their unique IDs.
        """
        return {k: v for k, v in self.manifest.nodes.items() if str(v.resource_type).lower() == "model"}
