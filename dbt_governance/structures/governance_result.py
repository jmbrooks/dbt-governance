from typing import List

from pydantic import BaseModel, ConfigDict, Field

import dbt_governance.constants as constants
from dbt_governance.structures.validation_result import ValidationResult


class GovernanceResultMetadata(BaseModel):
    """Metadata about the governance evaluation."""

    model_config = ConfigDict(frozen=True)

    generated_at: str = Field(..., description="The timestamp when the governance evaluation was generated.")
    result_uuid: str = Field(..., description="The UUID of the governance evaluation result.")
    dbt_governance_version: str = Field(
        ..., description=f"The version of {constants.PROJECT_NAME} used for the evaluation."
    )


class GovernanceResultSummary(BaseModel):
    """Summary statistics about the governance evaluation."""

    total_evaluations: int = Field(..., description="Total number of governance evaluations performed this run.")
    total_passed: int = Field(..., description="Total number of governance evaluations that passed this run.")
    total_failed: int = Field(..., description="Total number of governance evaluations that failed this run.")

    @property
    def pass_rate(self) -> float:
        """Calculate the pass rate of the governance evaluation."""
        return self.total_passed / self.total_evaluations if self.total_evaluations > 0 else 0.0


class GovernanceResult(BaseModel):
    """Represent the full governance result artifact.

    Attributes:
        summary (GovernanceResultSummary): A summary of the governance results (e.g., total passed/failed).
        metadata (GovernanceResult): Metadata about the evaluation (e.g., timestamp, dbt version).
        results (List[ValidationResult]): List of Validation check results detailed for each rule evaluation.
    """

    summary: GovernanceResultSummary = Field(..., description="Summary statistics about the governance evaluation.")
    metadata: GovernanceResultMetadata = Field(..., description="Metadata about the governance evaluation.")
    results: List[ValidationResult] = Field(..., description="List of validation results for each rule evaluation.")

    def to_dict(self) -> dict:
        """Convert the GovernanceResult to a dictionary for JSON serialization."""
        result_dict = self.model_dump()
        result_dict["results"] = [detail.to_dict() for detail in self.results]
        return result_dict
