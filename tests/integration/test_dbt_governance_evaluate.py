from pathlib import Path
from click.testing import CliRunner

from dbt_governance.cli import cli


def test_dbt_governance_evaluate_integration(mock_dbt_project: Path, mock_rules_file: Path, tmp_path: Path) -> None:
    """Test the end-to-end functionality of the `dbt-governance evaluate` CLI."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "evaluate",
            "--project-path", str(mock_dbt_project),
            "--rules-file", str(mock_rules_file),
        ],
    )

    # Assertions on CLI output
    assert result.exit_code == 0
    assert "Governance Evaluation Results:" in result.output
    assert "JSON results written to" in result.output
