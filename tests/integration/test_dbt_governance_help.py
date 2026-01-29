from pathlib import Path

from click.testing import CliRunner

from dbt_governance.cli import cli


def test_dbt_governance_no_args_help(mock_dbt_project: Path, mock_rules_file: Path, tmp_path: Path) -> None:
    """Test the functionality of the `dbt-governance` command, returning help output."""
    runner = CliRunner()

    result = runner.invoke(cli)

    # Assertions on CLI output
    assert result.exit_code == 2  # Click gives error code 2 when no --help provided, expected
    assert "dbt Governance Tool" in result.output
    assert "-V, --version" in result.output
    assert "--help" in result.output
    assert "evaluate" in result.output
    assert "list-rules" in result.output
    assert "validate-config" in result.output
