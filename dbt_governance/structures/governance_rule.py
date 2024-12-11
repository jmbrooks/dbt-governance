from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dbt_governance.structures.severity import Severity


@dataclass
class GovernanceRule:
    """Represents a governance rule to evaluate dbt projects."""

    name: str
    description: str
    severity: Severity
    enabled: Optional[bool] = True
    paths: Optional[List[str]] = None  # Affected paths (e.g., folders/models)
    checks: Optional[Dict[str, Any]] = None  # Specific check details (e.g., test types)

    @classmethod
    def from_dict(cls, rule_data: Dict[str, Any]) -> "GovernanceRule":
        """Create a GovernanceRule object from a dictionary."""
        return cls(
            name=rule_data.get("name"),
            description=rule_data.get("description"),
            severity=Severity(rule_data.get("severity")),
            enabled=rule_data.get("enabled", True),
            paths=rule_data.get("paths"),
            checks=rule_data.get("checks"),
        )

    @classmethod
    def get_rule_by_name(cls, rule_name: str, rules_data: List[Dict[str, Any]]) -> "GovernanceRule":
        """Retrieve a governance rule by its name."""
        rule_index = next((i for i, item in enumerate(rules_data) if item.get("name") == rule_name), -1)
        if rule_index == -1:
            raise ValueError(f"Rule not found in rules config data: {rule_name}")
        return GovernanceRule(
            name=rule_name,
            description=rules_data[rule_index].get("description"),
            severity=rules_data[rule_index].get("severity"),
            enabled=rules_data[rule_index].get("enabled", True),
        )
