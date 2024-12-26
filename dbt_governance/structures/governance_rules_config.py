from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

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
        return cls(
            rule_evaluation_config=RuleEvaluationConfig.from_dict(rules_config_data.get("rule_evaluation_config", {})),
            rules=[GovernanceRule(**rule_data) for rule_data in rules_config_data.get("rules", [])],
        )
