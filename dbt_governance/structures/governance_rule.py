from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

import dbt_governance.utils as utils
from dbt_governance.structures.severity import Severity


class GovernanceRuleCheckType(BaseModel):
    type: str
    description: Optional[str] = None


class GovernanceRule(BaseModel):
    """Represents a governance rule to evaluate dbt projects."""

    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(..., description="The name of the rule.")
    type: str = Field(..., description="The type of evaluation rule.")
    description: str = Field(..., description="A description of the rule.")
    severity: Severity = Field(..., description="The severity level of the rule.")
    enabled: Optional[bool] = Field(True, description="Whether the rule is enabled.")
    args: Optional[Dict[str, Any]] = Field(None, description="Test-specific arguments or argument scope configuration.")
    paths: Optional[List[str]] = Field(None, description="Affected paths (e.g., folders/models).")

    @classmethod
    def from_dict(cls, rule_data: Dict[str, Any]) -> "GovernanceRule":
        """Create a GovernanceRule object from a dictionary."""
        return cls(
            name=rule_data.get("name"),
            type=rule_data.get("type"),
            description=rule_data.get("description"),
            severity=Severity(rule_data.get("severity")),
            enabled=rule_data.get("enabled", True),
            paths=rule_data.get("paths"),
            args=rule_data.get("args"),
        )

    @classmethod
    def get_rule_by_name(cls, rule_name: str, rules_data: List[Dict[str, Any]]) -> "GovernanceRule":
        """Retrieve a governance rule by its name."""
        rule_index = next((i for i, item in enumerate(rules_data) if item.get("name") == rule_name), -1)
        if rule_index == -1:
            raise ValueError(f"Rule not found in rules config data: {rule_name}")
        return cls(
            name=rule_name,
            type=rules_data[rule_index].get("type"),
            description=rules_data[rule_index].get("description"),
            severity=rules_data[rule_index].get("severity"),
            enabled=rules_data[rule_index].get("enabled", True),
            args=rules_data[rule_index].get("args"),
        )

    @property
    def dbt_selection_clause(self) -> str:
        """Generate a dbt selection clause for the rule."""
        selection_clause = ""
        if self.args:
            select_clause = self.args.get("select", "")
            exclude_clause = self.args.get("exclude", "")
            selection_clause = utils.assemble_dbt_selection_clause(select_clause, exclude_clause)
        return selection_clause
