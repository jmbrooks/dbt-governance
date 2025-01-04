from pathlib import Path

from click.testing import CliRunner

from dbt_governance.cli import cli


def test_dbt_governance_validate_config(mock_governance_config_file: Path) -> None:
    """Test the end-to-end functionality of the `dbt-governance validate-config` CLI."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args=[
            "validate-config",
            "--config-file",
            str(mock_governance_config_file),
        ],
    )

    # Assertions on CLI output
    assert result.exit_code == 0
    assert "Configuration file is valid!" in result.output
