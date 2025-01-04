import click

import dbt_governance.constants as constants
import dbt_governance.utils as utils
from dbt_governance import __version__
from dbt_governance.logging_config import green, logger, red, yellow
from dbt_governance.rules.registry import register_rule
from dbt_governance.structures.evaluate_runner import EvaluateRunner
from dbt_governance.structures.governance_config import GovernanceConfig
from dbt_governance.structures.governance_rules_config import GovernanceRulesConfig
from dbt_governance.structures.severity import Severity
from dbt_governance.structures.validation_result import ValidationStatus
from dbt_governance.tasks import evaluate_task, list_rules_task, validate_config_task


@click.group(no_args_is_help=True)
@click.version_option(__version__, "--version", "-V", prog_name=constants.PROJECT_NAME)
def cli() -> click.BaseCommand:
    """dbt Governance Tool: Manage and enforce governance rules for dbt projects."""


@cli.command()
@click.option(
    "--project-path",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Path to a single dbt project directory.",
)
@click.option(
    "--project-paths",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    multiple=True,
    help="Paths to one or more dbt project directories.",
)
@click.option(
    "--rules-file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="Path to a custom rules file.",
)
@click.option(
    "--severity",
    type=click.Choice([severity.value for severity in Severity]),
    # nargs=-1,
    multiple=True,
    help="Filter results by one or more severities (e.g., 'critical', 'high', 'medium', 'low').",
)
def evaluate(project_path: str, project_paths: list[str], rules_file: str, severity: str) -> None:
    """Run governance checks on the specified dbt project(s).

    Args:
        project_path (str): Path to a single dbt project directory.
        project_paths (list[str]): Paths to one or more dbt project directories.
        rules_file (str): Valid path to a custom rules file.
        severity (str): The severity or severities to limit the evaluation task to.

    Returns:
        None.
    """
    config = GovernanceConfig.load_config(project_path, project_paths, rules_file)
    evaluate_run_instance = EvaluateRunner()
    output_file_path = config.output_path

    click.echo(f"Running dbt-governance v{__version__} evaluation with UUID: {evaluate_run_instance.run_uuid}")
    logger.debug(f"Running governance checks with configuration: {config}")

    # Load rules configuration
    governance_rules_config = GovernanceRulesConfig.from_yaml_file(config.global_rules_file)
    logger.debug(f"Loaded governance rules config: {governance_rules_config}")

    # Filter rules by severity, if specified
    rules = governance_rules_config.rules
    if severity:
        logger.info(f"Limiting severity to {', '.join(severity)}")
        rules = [rule for rule in rules if str(rule.severity) in severity]

    # Register all selected and enabled rules
    for rule in rules:
        register_rule(rule=rule)

    # Get scope of dbt projects to evaluate
    project_paths = config.get_project_paths()
    click.echo(f"dbt-governance project path(s) scope: {', '.join(str(path) for path in project_paths)}")

    # Evaluate configured and selected rules against dbt project(s)
    governance_evaluation = evaluate_task(
        evaluate_run_instance,
        rules,
        project_paths,
        evaluate_run_instance.run_uuid,
        __version__,
    )
    logger.debug("Rule evaluations completed")

    # Output results

    # Check pass rate acceptance thresholds, if configured
    # Aggregate results by severity
    severity_summary = {}
    for result in governance_evaluation.results:
        severity = str(result.rule_severity)
        if severity not in severity_summary:
            severity_summary[severity] = {"evaluated": 0, "passed": 0}
        severity_summary[severity]["evaluated"] += 1
        if result.status == ValidationStatus.PASSED.value:
            severity_summary[severity]["passed"] += 1

    # Compute overall pass rate
    total_evaluated = sum(data["evaluated"] for data in severity_summary.values())
    total_passed = sum(data["passed"] for data in severity_summary.values())
    overall_pass_rate = (total_passed / total_evaluated) * 100 if total_evaluated > 0 else 100

    click.echo("\nGovernance Evaluation Results:")

    # Check pass rate acceptance thresholds
    thresholds = governance_rules_config.rule_evaluation_config.pass_rate_acceptance_thresholds
    if thresholds:
        click.echo("\nPass Rate Acceptance By Severity:")
        for severity, data in severity_summary.items():
            evaluated = data["evaluated"]
            passed = data["passed"]
            pass_rate = (passed / evaluated) * 100 if evaluated > 0 else 100
            threshold = getattr(thresholds, severity, None)

            if threshold is not None:
                threshold_met = pass_rate >= threshold
                threshold_met_comparison = "meets" if threshold_met else "below"
                pass_rate_display = green(f"{pass_rate:.2f}%") if threshold_met else red(f"{pass_rate:.2f}%")
                click.echo(
                    f"  {severity.capitalize()} Severity - Passed: {passed}, Evaluated: {evaluated}, Pass Rate: "
                    f"{pass_rate_display} ({threshold_met_comparison} acceptance threshold of {threshold}%)"
                )
            else:
                click.echo(
                    f"  {severity.capitalize()} - Passed: {passed}, Evaluated: {evaluated}, Pass Rate: "
                    f"{pass_rate:.2f}% (No threshold set)"
                )

    click.echo("\nSummary:")
    click.echo(f"  Total Evaluations: {governance_evaluation.summary.total_evaluations}")
    click.echo(f"  Total Passed: {governance_evaluation.summary.total_passed}")
    click.echo(f"  Total Failed: {governance_evaluation.summary.total_failed}")

    if governance_evaluation.summary.total_evaluations == 0:
        click.echo(yellow("\nNo rules evaluated in this dbt-governance run."))
    else:
        # click.echo(f"\nOverall Pass Rate: {governance_evaluation.summary.pass_rate:.2%}")
        # Check overall threshold
        overall_threshold = thresholds.overall
        if overall_threshold is not None:
            threshold_met = overall_pass_rate >= overall_threshold
            comparison = "meets" if threshold_met else "below"
            pass_rate_display = (
                green(f"{overall_pass_rate:.2f}%") if threshold_met else red(f"{overall_pass_rate:.2f}%")
            )
            click.echo(
                f"\nOverall - Pass Rate: {pass_rate_display} ({comparison} overall acceptance threshold of "
                f"{overall_threshold}%)"
            )
        else:
            click.echo(f"  Overall - Pass Rate: {overall_pass_rate:.2f} (No threshold set)")
        if governance_evaluation.summary.total_evaluations == governance_evaluation.summary.total_passed:
            click.echo(green("\nAll rule evaluations passed!"))

    # Write to JSON file
    utils.write_json_result(governance_evaluation.to_dict(), output_file_path)
    utils.write_json_result(governance_evaluation.to_dict(), output_file_path)
    click.echo(f"\nJSON results written to {output_file_path}")


# Command: List Governance Rules
@cli.command()
@click.option(
    "--project-path",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Path to a single dbt project directory.",
)
@click.option(
    "--project-paths",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    multiple=True,
    help="Paths to one or more dbt project directories.",
)
@click.option(
    "--rules-file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="Path to a custom rules file.",
)
def list_rules(project_path: str, project_paths: list[str], rules_file: str) -> None:
    """List all configured and enabled governance rules.

    Args:
        project_path (str): Path to single dbt project directory.
        project_paths (list[str]): Paths to one or more dbt project directories.
        rules_file (str): Path to custom rules file.

    Returns:
        None.
    """
    click.echo("Listing active governance rules...")
    governance_rules = list_rules_task(project_path, project_paths, rules_file)
    for rule in governance_rules:
        click.echo(f"- {rule.name} (Severity: {rule.severity}): {rule.description}")


# Command: Validate Configuration File
@cli.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    default=constants.DEFAULT_CONFIG_PATH,
    help="Path to the configuration file to validate.",
)
def validate_config(config_file: str) -> None:
    """Validate the dbt-governance project configuration file.

    Args:
        config_file (str): Path to configuration file.

    Returns:
        None.
    """
    click.echo(f"Validating configuration file: {config_file}")

    is_valid, valid_config_message = validate_config_task(config_file)

    if not is_valid:
        click.echo("Configuration validation failed with the following errors:")

    click.echo(valid_config_message)


if __name__ == "__main__":
    cli()
