from pathlib import Path

import pytest


@pytest.fixture()
def mock_dbt_project(tmp_path: Path) -> Path:
    """Set up a temporary dbt project with necessary files."""
    project_path = tmp_path / "dbt_project"
    project_path.mkdir(parents=True, exist_ok=True)

    # Create dbt_project.yml
    (project_path / "dbt_project.yml").write_text(
        """
        name: mock_project
        version: 1.0.0
        profile: default
        """
    )

    # Create target directory with a mock manifest.json
    target_dir = project_path / "target"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "manifest.json").write_text("{}")  # Empty mock manifest

    return project_path


@pytest.fixture()
def mock_rules_file(tmp_path: Path) -> Path:
    """Set up a temporary rules file."""
    rules_file = tmp_path / "rules.yml"
    rules_file.write_text(
        """
        rules:
          - name: Primary Key Test
            type: data
            description: Ensure primary key tests are defined.
            severity: high
            enabled: true
          - name: Owner Metadata
            type: metadata
            description: Ensure all models have an owner defined.
            severity: medium
            enabled: true
        """
    )
    return rules_file
