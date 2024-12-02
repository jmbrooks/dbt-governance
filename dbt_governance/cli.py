import click
import yaml
from dbt_governance.check import load_rules, evaluate_rules
from dbt_governance.constants import DEFAULT_CONFIG_PATH
from dbt_governance.logging_config import logger
from dbt_governance.config import load_config, validate_config_structure
from dbt_governance.structures.severity import Severity
from dbt_governance.structures.validation_result import ValidationStatus


@click.group()
def cli():
    """dbt Governance Tool: Manage and enforce governance rules for dbt projects."""
    pass


# Command: Check Governance Rules
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
    help="Filter results by severity (e.g., 'critical', 'high', 'medium', 'low').",
)
def check(project_path, project_paths, rules_file, severity):
    """Run governance checks on the specified dbt project(s)."""
    config = load_config(project_path, project_paths, rules_file)
    logger.info(f"Running governance checks with configuration: {config}")

    # Placeholder: Load rules
    rules = load_rules(config["global_rules_file"])
    logger.debug(f"Loaded rules: {rules}")

    # Filter rules by severity, if specified
    if severity:
        rules = [rule for rule in rules if rule.severity.value == severity]

    # Placeholder: Evaluate rules
    results = evaluate_rules(rules, config["project_paths"])
    logger.info("Rule evaluation results: %s", results)

    # Output results
    click.echo("Governance Check Results:")
    summary = {status: 0 for status in ValidationStatus}
    for result in results:
        summary[result.status] += 1
        click.echo(f"- Rule: {result.rule_name} - Status: {result.status.value}")
        if result.reason:
            click.echo(f"  Reason: {result.reason}")

    click.echo("\nSummary:")
    for status, count in summary.items():
        click.echo(f"{status.value.title()}: {count}")


# Command: List Governance Rules
@cli.command()
def list_rules():
    """List active governance rules."""
    click.echo("Listing active governance rules...")
    example_rules = [
        {"name": "Primary Key Test", "severity": "High", "description": "Ensure primary key tests on all models."},
        {"name": "Owner Metadata", "severity": "Medium", "description": "Ensure all models have an 'owner' meta property."},
    ]
    for rule in example_rules:
        click.echo(f"- {rule['name']} (Severity: {rule['severity']}): {rule['description']}")


# Command: Validate Configuration File
@cli.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    default=DEFAULT_CONFIG_PATH,
    help="Path to the configuration file to validate.",
)
def validate_config(config_file: str):
    """Validate the configuration file."""
    click.echo(f"Validating configuration file: {config_file}")
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        click.echo(f"YAML Parsing Error: {e}", err=True)
        return
    except Exception as e:
        click.echo(f"Failed to load configuration file: {e}", err=True)
        return

    errors = validate_config_structure(config)
    if errors:
        click.echo("Configuration validation failed with the following errors:")
        for error in errors:
            click.echo(f"- {error}", err=True)
    else:
        click.echo("Configuration file is valid!")
    # Log the loaded configuration (sensitive keys redacted)
    redacted_config = config.copy()
    if "dbt_cloud" in redacted_config and "api_token" in redacted_config["dbt_cloud"]:
        redacted_config["dbt_cloud"]["api_token"] = "REDACTED"  # nosec B105 (no hardcode issue, false flag)
    logger.info("Loaded Configuration: %s", redacted_config)


if __name__ == "__main__":
    cli()
