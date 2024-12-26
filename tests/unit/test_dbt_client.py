import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dbt.contracts.graph.manifest import Manifest

from dbt_governance.dbt_project import DbtProject


def test_manifest_loading(dbt_client: DbtProject, mock_manifest_data: dict, tmp_path: Path) -> None:
    """Test loading a manifest file."""
    manifest_path = tmp_path / "dbt_project" / "target" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Write mock manifest data to the file
    with open(manifest_path, "w") as f:
        json.dump(mock_manifest_data, f)

    # Mock the Manifest.from_dict method
    with patch("dbt_governance.dbt_client.Manifest.from_dict") as mock_from_dict:
        mock_manifest = MagicMock(spec=Manifest)
        mock_from_dict.return_value = mock_manifest

        # Call load_manifest and verify the mock was called
        loaded_manifest = dbt_client.load_manifest()
        mock_from_dict.assert_called_once_with(mock_manifest_data)
        assert loaded_manifest == mock_manifest


def test_manifest_file_not_found(dbt_client: DbtProject) -> None:
    """Test behavior when the manifest file is not found."""
    with pytest.raises(FileNotFoundError, match="Manifest file not found"):
        dbt_client.load_manifest()


def test_dbt_version(dbt_client: DbtProject, mock_manifest_data: dict, tmp_path: Path) -> None:
    """Test retrieving the dbt version from the manifest."""
    manifest_path = tmp_path / "dbt_project" / "target" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Write mock manifest data to the file
    with open(manifest_path, "w") as f:
        json.dump(mock_manifest_data, f)

    # Mock the Manifest.from_dict method
    with patch("dbt_governance.dbt_client.Manifest.from_dict") as mock_from_dict:
        mock_metadata = MagicMock()
        mock_metadata.dbt_version = "1.8.0"

        mock_manifest = MagicMock(spec=Manifest)
        mock_manifest.metadata = mock_metadata
        mock_from_dict.return_value = mock_manifest

        assert dbt_client.dbt_version == "1.8.0"


def test_generated_at(dbt_client: DbtProject, mock_manifest_data: dict, tmp_path: Path) -> None:
    """Test retrieving the generated_at timestamp from the manifest."""
    manifest_path = tmp_path / "dbt_project" / "target" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Write mock manifest data to the file
    with open(manifest_path, "w") as f:
        json.dump(mock_manifest_data, f)

    # Mock the Manifest.from_dict method
    with patch("dbt_governance.dbt_client.Manifest.from_dict") as mock_from_dict:
        mock_metadata = MagicMock()
        mock_metadata.generated_at = "2021-08-01T00:00:00.000Z"

        mock_manifest = MagicMock(spec=Manifest)
        mock_manifest.metadata = mock_metadata
        mock_from_dict.return_value = mock_manifest

        assert dbt_client.generated_at == "2021-08-01T00:00:00.000Z"


def test_get_model_nodes(dbt_client: DbtProject, mock_manifest_data: dict, tmp_path: Path) -> None:
    """Test retrieving model nodes from the manifest."""
    manifest_path = tmp_path / "dbt_project" / "target" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Write mock manifest data to the file
    with open(manifest_path, "w") as f:
        json.dump(mock_manifest_data, f)

    # Mock the Manifest.from_dict method
    with patch("dbt_governance.dbt_client.Manifest.from_dict") as mock_from_dict:
        # Mock manifest with nodes
        mock_manifest = MagicMock(spec=Manifest)

        # Create mock nodes
        mock_manifest.nodes = {
            "model.test_model_1": MagicMock(resource_type="model", name="test_model_1"),
            "model.test_model_2": MagicMock(resource_type="model", name="test_model_2"),
            "source.test_source_1": MagicMock(resource_type="source", name="test_source_1"),
        }
        # Set the return_value for each mock's `name` attribute
        mock_manifest.nodes["model.test_model_1"].name = "test_model_1"
        mock_manifest.nodes["model.test_model_2"].name = "test_model_2"
        mock_manifest.nodes["source.test_source_1"].name = "test_source_1"
        mock_from_dict.return_value = mock_manifest

        model_nodes = dbt_client.get_model_nodes()
        expected_nodes = {
            "model.test_model_1": {"resource_type": "model", "name": "test_model_1"},
            "model.test_model_2": {"resource_type": "model", "name": "test_model_2"},
        }
        # Convert Mock nodes to dict for comparison
        actual_nodes = {
            key: {"resource_type": node.resource_type, "name": node.name} for key, node in model_nodes.items()
        }
        assert actual_nodes == expected_nodes
