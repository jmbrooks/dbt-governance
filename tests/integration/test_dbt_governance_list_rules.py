from pathlib import Path

from click.testing import CliRunner

from dbt_governance.cli import cli


def test_dbt_governance_list_rules(mock_dbt_project: Path, mock_rules_file: Path, tmp_path: Path) -> None:
    """Test the end-to-end functionality of the `dbt-governance list-rules` CLI."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args=[
            "list-rules",
            "--project-path",
            str(mock_dbt_project),
            "--rules-file",
            str(mock_rules_file),
        ],
    )

    # Assertions on CLI output
    assert result.exit_code == 0
    assert "Listing active governance rules" in result.output
    assert "Primary Key Test" in result.output
    assert "Owner Metadata" in result.output
