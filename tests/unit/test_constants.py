from pathlib import Path

import dbt_governance.constants as constants


def test_constants() -> None:
    """Test that constants are set correctly."""
    # Static constants
    assert constants.PROJECT_NAME == "dbt-governance"
    assert constants.DEFAULT_OUTPUT_FILE_NAME == "governance-results.json"
    assert constants.DEFAULT_OWNER_META_PROPERTY_NAME == "owner"


def test_path_expansion() -> None:
    """Test that paths are expanded correctly."""
    home_dir = Path.expanduser(Path("~"))

    # Check expanded paths
    assert constants.DEFAULT_CONFIG_PATH == home_dir / ".dbt-governance/config.yml"
