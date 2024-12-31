from pathlib import Path
from typing import Any, Optional, Union

import yaml

from pydantic import BaseModel, ConfigDict, Field

from dbt_governance.logging_config import logger
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.severity import Severity


class PassRateAcceptanceThresholdsConfig(BaseModel):
    """Represents the pass rate acceptance thresholds for governance rules."""

    model_config = ConfigDict(frozen=True)

    overall: Optional[float] = Field(None, description="The overall pass rate threshold.")
    critical: Optional[float] = Field(None, description="The pass rate threshold for critical rules.")
    high: Optional[float] = Field(None, description="The pass rate threshold for high severity rules.")
    medium: Optional[float] = Field(None, description="The pass rate threshold for medium severity rules.")
    low: Optional[float] = Field(None, description="The pass rate threshold for low severity rules.")

    @classmethod
    def from_dict(cls, thresholds_config_data: dict[str, float]) -> "PassRateAcceptanceThresholdsConfig":
        return cls(
            overall=thresholds_config_data.get("overall"),
            critical=thresholds_config_data.get("critical"),
            high=thresholds_config_data.get("high"),
            medium=thresholds_config_data.get("medium"),
            low=thresholds_config_data.get("low"),
        )

    @property
    def has_set_any_thresholds(self) -> bool:
        """Return True if any thresholds have been set."""
        return any(threshold is not None for threshold in self.model_dump().values())


class RuleEvaluationConfig(BaseModel):
    """Represents the configuration options for evaluating governance rules.

    Attributes:
        default_severity (str): The default severity level for rules that do not specify a severity.
        pass_rate_acceptance_thresholds (PassRateAcceptanceThresholdsConfig): The pass rate acceptance thresholds.
    """

    default_severity: str = Field(Severity.default_rule_severity(), description="The default severity level for rules.")
    pass_rate_acceptance_thresholds: Optional[PassRateAcceptanceThresholdsConfig] = Field(
        None, description="Pass rate acceptance thresholds."
    )

    @classmethod
    def from_dict(cls, evaluation_config_data: dict[str, str]) -> "RuleEvaluationConfig":
        thresholds_config_data = evaluation_config_data.get("pass_rate_acceptance_thresholds", {})
        return cls(
            default_severity=evaluation_config_data.get("default_severity", Severity.default_rule_severity()),
            pass_rate_acceptance_thresholds=PassRateAcceptanceThresholdsConfig.from_dict(thresholds_config_data),
        )


class GovernanceRulesConfig(BaseModel):
    """Represents the configuration for governance rules."""

    rule_evaluation_config: RuleEvaluationConfig = Field(
        ..., description="The configuration options for evaluating governance"
    )
    rules: list[GovernanceRule] = Field(..., description="The governance rules to evaluate.")

    @classmethod
    def from_dict(cls, rules_config_data: dict[str, Any]) -> "GovernanceRulesConfig":
        """"""
        return cls(
            rule_evaluation_config=RuleEvaluationConfig.from_dict(rules_config_data.get("rule_evaluation_config", {})),
            rules=[GovernanceRule(**rule_data) for rule_data in rules_config_data.get("rules", [])],
        )

    @classmethod
    def from_yaml_file(
        cls, rules_file: Optional[Union[str, Path]], include_not_enabled: bool = False
    ) -> "GovernanceRulesConfig":
        """Load governance rules and thresholds from a YAML file.

        Args:
            rules_file (Union[str, Path]): Path to the rules file.
            include_not_enabled (bool): Default False; if set True, return both enabled and not enabled rules.
        Returns:
            GovernanceRulesConfig: A dataclass containing the rules and evaluation configuration.

        Raises:
            FileNotFoundError: If the configured governance rules config file is not found.
            ValueError: If the rules file cannot be loaded for any reason other than not being found.
        """
        rules_file = Path(rules_file) if rules_file else None
        if not rules_file or not Path.exists(rules_file):
            raise FileNotFoundError(f"Rules file not found: {rules_file}")

        try:
            with Path.open(rules_file, mode="r") as f:
                yaml_data = yaml.safe_load(f) or {}

            rule_evaluation_config_data = yaml_data.get("rule_evaluation_config", {})
            rules_data = yaml_data.get("rules", [])

            rule_evaluation_config = RuleEvaluationConfig.from_dict(rule_evaluation_config_data)
            rules = []
            for rule_data in rules_data:
                try:
                    rule = GovernanceRule.from_dict(rule_data)
                    if not include_not_enabled and not rule.enabled:
                        logger.debug(
                            f"Skipping rule '{rule.name}' as it not marked as enabled in the rules config.")
                        continue
                    rules.append(rule)
                except TypeError as e:
                    logger.error(f"Invalid rule format in rules file: {rule_data}. Error: {e}")

            return cls(
                rule_evaluation_config=rule_evaluation_config,
                rules=rules,
            )
        except Exception as err:
            raise ValueError(f"Failed to load governance rules: {err}") from err
