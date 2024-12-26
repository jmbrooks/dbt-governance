# dbt-governance

[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A flexible governance tool for [dbt](https://www.getdbt.com/) projects, enabling teams to define and enforce custom
rules for data quality, privacy, security, and compliance.

Supports single and multi-project [dbt mesh](https://www.getdbt.com/product/dbt-mesh) configurations, with integrations
for local development and planned compatibility with dbt Cloud.

Includes features for metadata validation, test coverage checks, and rule-based governance health reporting.

## Basic Usage

### Initial Setup

To get started, you'll need to configure your dbt project(s) to work with dbt-governance. This involves adding a new
global configuration file in your home directory, `~/.dbt-governance/config.yml`, with the following structure:

```yaml
# Path to your dbt project directory
project_path: /Users/jbbrooks/PycharmProjects/dbt-betterhelp
# Or specify multiple project paths, if you are using a dbt mesh design
project_paths: [
    'path/to/primary_dbt_project',
    'path/to/secondary_dbt_project'
]
# Path to your global governance rules file
global_rules_file: 'path/to/governance-rules.yml'
```

### Configure Rules

Next, you'll need to define your governance rules which you want your dbt project(s) to adhere to. This is typically
defined either in your dbt project root directly, or in `~/.dbt-governance/governance-rules.yml`. Here's an example
bare minimum `governance-rules.yml` file:

```yaml
rule_evaluation_config:
  default_severity: "medium"  # Default severity if not specified in a rule
  pass_rate_acceptance_thresholds:  # Pass rate percentage thresholds, by severity
    overall: 90  # Overall pass rate threshold, across all severities
    critical: 100
    high: 80
    medium: 60

# Define dbt governance rules
rules:
  - name: analytics_ready
    description: "Ensure all dbt models are tagged with 'analytics_ready'."
    severity: "high"
    type: "has_meta"
    args:
      required_property: "analytics_ready"
      exclude: "betterhelp.staging"
  - name: facts_have_fact_tag
    description: "Ensure all fact tables have the 'fact' tag."
    severity: "medium"
    type: "has_tag"
    args:
      required_tag: "fact"
      select: "fct_"
      match_type: "startswith"
  - name: "Owner Metadata"
    enabled: false
    description: "Ensure all dbt models specify an 'owner' in their meta property."
    severity: "high"
    type: "has_meta"
    args:
      required_property: "owner"
      select: "stg_"
  - name: "Primary Key Test"
    enabled: false
    description: "Ensure the column defined as the primary_key in the model's config has a unique test defined."
    severity: "high"
    type: "has_test"
    args:
      test_type: "primary_key"
```

### Evaluate Governance Rules

Once you have configured your rules, you can evaluate them against your dbt project(s) using `evaluate`:

```bash
dbt-governance evaluate
```

For more information on all options, commands and evaluation capabilities, run `dbt-governance --help`, or the `--help`
option for any individual command.

## Installation

Install the package using pip:

```bash
pip install dbt-governance
```

## Contributing

For guidance on contributing to dbt-governance and setting up your local development environment, review our
[Contributing Guide](CONTRIBUTING.md).
