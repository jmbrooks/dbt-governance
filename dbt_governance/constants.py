from pathlib import Path

PROJECT_NAME = "dbt-governance"

DEFAULT_CONFIG_PATH = Path.expanduser("~/.dbt-governance/config.yml")
DEFAULT_OUTPUT_FILE_NAME = "governance-results.json"
DEFAULT_RULES_FILE_NAME = "governance-rules.yml"

# dbt project rule defaults
DEFAULT_OWNER_META_PROPERTY_NAME = "owner"
