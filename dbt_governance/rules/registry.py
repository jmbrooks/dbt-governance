from typing import ClassVar, Optional

from dbt_governance.logging_config import logger
from dbt_governance.structures.governance_rule import GovernanceRule


class RulesRegistry:
    """Registry for default governance rules."""

    _rules: ClassVar[dict[str, GovernanceRule]] = {}
    _rule_selection_clauses: ClassVar[dict[str, dict[str, str]]] = {}

    @classmethod
    def register_rule(cls, rule: GovernanceRule) -> None:
        """Register a default governance rule."""
        if rule.name in cls._rules:
            raise ValueError(f"Rule with name '{rule.name}' is already registered.")
        cls._rules[rule.name] = rule
        if rule.args and ("select" in rule.args or "exclude" in rule.args):
            cls._rule_selection_clauses[rule.name] = {
                "select": rule.args.get("select", ""),
                "exclude": rule.args.get("exclude", ""),
            }

    @property
    def all_rules(self) -> list[GovernanceRule]:
        """Retrieve all registered default rules."""
        return list(self._rules.values())

    @property
    def rule_selection_clauses(self) -> dict[str, dict[str, str]]:
        """Retrieve all rule selection clauses."""
        return self._rule_selection_clauses

    @classmethod
    def get_rule(cls, rule_name: str) -> GovernanceRule:
        """Retrieve a registered rule by name."""
        if rule_name not in cls._rules:
            raise ValueError(f"Rule with name '{rule_name}' is not registered.")
        return cls._rules[rule_name]

    @classmethod
    def get_distinct_rule_selection_clauses(cls) -> set[str]:
        """Retrieve distinct rule selection clauses."""
        selection_clauses = set()
        for rule_name, rule_data in cls._rule_selection_clauses.items():
            selection_clause_string = ""
            select_clause = rule_data.get("select")
            exclude_clause = rule_data.get("exclude")
            if select_clause or exclude_clause:
                selections = select_clause.split()
                sorted_selections = sorted(selections)
                sorted_select_clause = " ".join(sorted_selections)

                exclusions = exclude_clause.split()
                sorted_exclusions = sorted(exclusions)
                sorted_exclude_clause = " ".join(sorted_exclusions)

                if sorted_select_clause:
                    selection_clause_string += f" --select {sorted_select_clause}"
                if sorted_exclude_clause:
                    selection_clause_string += f" --exclude {sorted_exclude_clause}"

                logger.debug(f"Rule: {rule_name} registered with Selection Clause: {selection_clause_string}")
                selection_clauses.add(selection_clause_string)

        return selection_clauses


# Register default rules
# RulesRegistry.register_rule(
#     GovernanceRule(
#         name="Owner Metadata",
#         type="metadata",
#         description="Ensure all models have an owner defined in metadata.",
#         severity=Severity.HIGH,
#         enabled=True,
#         args={"required_meta_keys": ["owner"]},
#     )
# )
#
# RulesRegistry.register_rule(
#     GovernanceRule(
#         name="Primary Key Test",
#         type="test",
#         description="Ensure all models have a primary key test.",
#         severity=Severity.CRITICAL,
#         enabled=True,
#         paths=["models/core", "models/marts"],
#     )
# )
#
# RulesRegistry.register_rule(
#     GovernanceRule(
#         name="Not Null Test",
#         type="test",
#         description="Ensure all critical fields have a not null test.",
#         severity=Severity.HIGH,
#         enabled=True,
#         args={
#             "select": "project.staging",
#         },
#     )
# )


def register_rule(
    type: Optional[str] = None,
    severity=None,
    description: Optional[str] = None,
    name: Optional[str] = None,
    enabled: bool = True,
    rule: Optional[GovernanceRule] = None,
    **kwargs,
) -> callable:
    """Decorator to register a governance rule with RulesRegistry."""

    def decorator(func: callable) -> callable:
        # Create and register the rule
        if rule:
            governance_rule = GovernanceRule()
        else:
            governance_rule = GovernanceRule(
                name=name or func.__name__,
                type=type,
                severity=severity,
                description=description,
                enabled=enabled,
                args=kwargs.get("args", None),
                paths=kwargs.get("paths", None),
            )
        RulesRegistry.register_rule(governance_rule)

        # Return the original function
        return func

    return decorator
