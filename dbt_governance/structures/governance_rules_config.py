from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.severity import Severity


@dataclass
class PassRateAcceptanceThresholdsConfig:
    """Represents the pass rate acceptance thresholds for governance rules."""
    overall: Optional[float]
    critical: Optional[float]
    high: Optional[float]
    medium: Optional[float]
    low: Optional[float]

    @classmethod
    def from_dict(cls, thresholds_config_data: Dict[str, float]) -> "PassRateAcceptanceThresholdsConfig":
        return cls(
            overall=thresholds_config_data.get("overall"),
            critical=thresholds_config_data.get("critical"),
            high=thresholds_config_data.get("high"),
            medium=thresholds_config_data.get("medium"),
            low=thresholds_config_data.get("low"),
        )


@dataclass
class RuleEvaluationConfig:
    """"""
    default_severity: str = Severity.default_rule_severity()
    pass_rate_acceptance_thresholds: Optional[PassRateAcceptanceThresholdsConfig] = None

    @classmethod
    def from_dict(cls, evaluation_config_data: Dict[str, str]) -> "RuleEvaluationConfig":
        thresholds_config_data = evaluation_config_data.get("pass_rate_acceptance_thresholds", {})
        return cls(
            default_severity=evaluation_config_data.get("default_severity", Severity.default_rule_severity()),
            pass_rate_acceptance_thresholds=PassRateAcceptanceThresholdsConfig.from_dict(thresholds_config_data),
        )


@dataclass
class GovernanceRulesConfig:
    """Represents the configuration for governance rules."""
    rule_evaluation_config: RuleEvaluationConfig
    rules: List[GovernanceRule]

    @classmethod
    def from_dict(cls, rules_config_data: Dict[str, Any]) -> "GovernanceRulesConfig":
        return cls(
            rule_evaluation_config=RuleEvaluationConfig.from_dict(rules_config_data.get("rule_evaluation_config", {})),
            rules=[GovernanceRule(**rule_data) for rule_data in rules_config_data.get("rules", [])],
        )
