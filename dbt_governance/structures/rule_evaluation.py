from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.validation_result import ValidationResult


class RuleEvaluation(BaseModel):
    """Represents an instance of an evaluation of a governance rule."""

    model_config = ConfigDict(strict=True)

    rule: GovernanceRule = Field(..., description="The governance rule being evaluated.")
    dbt_project_path: str = Field(..., description="The path to the dbt project directory.")
    dbt_project_version: str = Field(..., description="The dbt version for the project being evaluated.")
    dbt_project_manifest_generated_at: str = Field(
        ..., description="The timestamp when the dbt project manifest was generated."
    )
    dbt_selection_syntax: Optional[str] = Field(
        None, description="The dbt selection syntax used to get dbt nodes to evaluate."
    )
    evaluate_dbt_nodes: list[str] = Field(
        [], description="The dbt nodes that will be / were evaluated by the rule this run."
    )
    validation_results: list[ValidationResult] = Field([], description="The results of the rule validation runs.")

    def to_dict(self) -> dict:
        """Convert the RuleEvaluation to a dictionary for JSON serialization."""
        return self.model_dump()
