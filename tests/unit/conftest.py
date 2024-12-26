import json
from pathlib import Path
from typing import Any

import pytest

from dbt_governance.dbt_project import DbtProject


@pytest.fixture()
def mock_manifest_data() -> Any:
    """Fixture to provide mock manifest data."""
    return {
        "metadata": {"dbt_version": "1.8.0"},
        "nodes": {
            "model.test_model_1": {"resource_type": "model", "name": "test_model_1"},
            "model.test_model_2": {"resource_type": "model", "name": "test_model_2"},
            "source.test_source_1": {"resource_type": "source", "name": "test_source_1"},
        },
    }


@pytest.fixture()
def dbt_client(tmp_path: Path) -> DbtProject:
    """Fixture to provide a DbtProject with a temporary project path."""
    project_path = tmp_path / "dbt_project"
    project_path.mkdir(parents=True, exist_ok=True)
    return DbtProject(project_path)


@pytest.fixture()
def sample_manifest() -> Any:
    """Fixture for loading a sample manifest.json."""
    manifest_path = Path("tests/resources/sample_project/target/manifest3.json")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Sample manifest file not found at {manifest_path}")

    with open(manifest_path, "r") as f:
        return json.load(f)


@pytest.fixture()
def tmp_manifest(tmp_path: Path, sample_manifest: str) -> Path:
    """Fixture for creating a temporary manifest.json for isolated tests."""
    sample_project = tmp_path / "sample_project"
    target_dir = sample_project / "target"
    target_dir.mkdir(parents=True)
    manifest_path = target_dir / "manifest3.json"
    with open(manifest_path, "w") as f:
        json.dump(sample_manifest, f)
    return Path(manifest_path)
