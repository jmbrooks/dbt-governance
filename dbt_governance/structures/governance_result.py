from dataclasses import asdict, dataclass, field
from typing import List

from dbt_governance.structures.validation_result import ValidationResult


@dataclass(frozen=True)
class GovernanceResultMetadata:
    """Metadata about the governance evaluation."""

    generated_at: str
    result_uuid: str
    dbt_governance_version: str


@dataclass(frozen=True)
class GovernanceResultSummary:
    """Summary statistics about the governance evaluation."""

    total_evaluations: int
    total_passed: int
    total_failed: int

    @property
    def pass_rate(self) -> float:
        """Calculate the pass rate of the governance evaluation."""
        return self.total_passed / self.total_evaluations if self.total_evaluations > 0 else 0.0


@dataclass
class GovernanceResult:
    """Represent the full governance result artifact.

    Attributes:
        summary (GovernanceResultSummary): A summary of the governance results (e.g., total passed/failed).
        metadata (GovernanceResult): Metadata about the evaluation (e.g., timestamp, dbt version).
        results (List[ValidationResult]): List of Validation check results detailed for each rule evaluation.
    """

    summary: GovernanceResultSummary
    metadata: GovernanceResultMetadata
    results: List[ValidationResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert the GovernanceResult to a dictionary for JSON serialization."""
        result_dict = asdict(self)
        result_dict["results"] = [detail.to_dict() for detail in self.results]
        return result_dict
