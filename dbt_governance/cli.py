import click

import dbt_governance.constants as constants
import dbt_governance.utils as utils
from dbt_governance import __version__
from dbt_governance.structures.governance_config import GovernanceConfig
from dbt_governance.initialize import load_rules
from dbt_governance.logging_config import green, logger, red, yellow
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
    """Run governance checks on the specified dbt project(s)."""
    config = GovernanceConfig.load_config(project_path, project_paths, rules_file)
    output_file_path = config.output_path
    check_uuid = utils.get_uuid()

    click.echo(f"Running dbt-governance v{__version__} check with UUID: {check_uuid}")
    logger.debug(f"Running governance checks with configuration: {config}")

    # Load rules configuration
    governance_rules_config = load_rules(config.global_rules_file)
    logger.debug(f"Loaded governance rules config: {governance_rules_config}")

    # Filter rules by severity, if specified
    rules = governance_rules_config.rules
    if severity:
        logger.info(f"Limiting severity to {', '.join(severity)}")
        rules = [rule for rule in rules if str(rule.severity) in severity]

    # Get scope of dbt projects to evaluate
    project_paths = config.get_project_paths()
    click.echo(f"dbt-governance project path(s) scope: {', '.join(str(path) for path in project_paths)}")

    # Evaluate configured and selected rules against dbt project(s)
    governance_evaluation = evaluate_task(rules, project_paths, check_uuid, __version__)
    logger.debug(f"Rule evaluation results: {governance_evaluation}")

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
    """List all configured and enabled governance rules."""
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
    """Validate the dbt-governance project configuration file."""
    click.echo(f"Validating configuration file: {config_file}")

    is_valid, valid_config_message = validate_config_task(config_file)

    if not is_valid:
        click.echo("Configuration validation failed with the following errors:")

    click.echo(valid_config_message)

    # try:
    #     with open(config_file, mode="r") as f:
    #         config = yaml.safe_load(f)
    # except yaml.YAMLError as e:
    #     click.echo(f"YAML Parsing Error: {e}", err=True)
    #     return
    # except Exception as e:
    #     click.echo(f"Failed to load configuration file: {e}", err=True)
    #     return
    #
    # errors = validate_config_structure(config)
    # if errors:
    #     click.echo("Configuration validation failed with the following errors:")
    #     for error in errors:
    #         click.echo(f"- {error}", err=True)
    # else:
    #     click.echo(green("Configuration file is valid!"))
    #
    # # Log the loaded configuration (sensitive keys redacted)
    # redacted_config = config.copy()
    # if redacted_config and "api_token" in redacted_config.get("dbt_cloud"):
    #     redacted_config["dbt_cloud"]["api_token"] = "REDACTED"  # nosec B105 (no hardcode issue, false flag)
    # logger.debug(f"Loaded Configuration: {redacted_config}")


if __name__ == "__main__":
    cli()
