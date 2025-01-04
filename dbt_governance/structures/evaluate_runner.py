from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PrivateAttr

import dbt_governance.utils as utils
from dbt_governance.structures.evaluation_status import EvaluationStatus
from dbt_governance.structures.governance_result import GovernanceResultMetadata
from dbt_governance.structures.governance_rule import GovernanceRule
from dbt_governance.structures.rule_evaluation import RuleEvaluation
from dbt_governance.structures.validation_result import ValidationResult, ValidationStatus


class EvaluateRunner(BaseModel):
    """Run a dbt governance evaluation against configured governance rules and capture results.

    Attributes:
        run_status (EvaluationStatus): The status of the evaluation run
        run_started_at (datetime): The date and time the run started (in UTC)
        dbt_project_scope (Optional[list[str]]): The list of dbt project scopes to run the evaluation against.
        rule_evaluation (RuleEvaluation): The rule evaluation configuration this run.
        metadata (Optional[GovernanceResultMetadata]): Metadata about the evaluation run.
    """

    run_status: EvaluationStatus = Field(EvaluationStatus.INITIALIZATION, description="Status of the evaluation run")
    run_started_at: datetime = Field(utils.get_utc_iso_timestamp(), description="Started time of the evaluation run")
    dbt_project_scope: Optional[list[str]] = Field(None, description="List dbt project names included in this run")
    rule_evaluation: Optional[RuleEvaluation] = Field(None, description="List of dbt rule evaluations executed")
    metadata: Optional[GovernanceResultMetadata] = Field(None, description="Metadata about the run")
    _run_uuid: Optional[str] = PrivateAttr(None)

    @property
    def run_uuid(self) -> str:
        """Return the universally unique identifier (UUID) string for the run instance."""
        return self._run_uuid if self._run_uuid else utils.get_uuid()

    def append_rule_evaluation_result(
        self,
        rule_evaluation_index: int,
        is_passing_evaluation: bool,
        rule: GovernanceRule,
        project_path: str,
        node_resource_type: str,
        node_unique_id: str,
        evaluation_description: Optional[str] = None,
    ) -> None:
        """Append a ValidationResult object to the results list for any rule evaluation.

        Args:
            rule_evaluation_index (int): Index of the rule evaluation in the RuleEvaluations list to append result to.
            is_passing_evaluation (bool): Whether the evaluation passed or failed.
            rule (GovernanceRule): The rule to validate.
            project_path (str): The path to the dbt project directory.
            node_resource_type (str): The dbt resource type (e.g. model, source, snapshot).
            node_unique_id (str): The unique ID of the dbt resource.
            evaluation_description (str): Optional reason for the passed or failed evaluation.
        """
        self.rule_evaluation.validation_results.append(
            ValidationResult(
                rule_name=rule.name,
                rule_severity=rule.severity,
                dbt_project_path=project_path,
                resource_type=node_resource_type,
                unique_id=node_unique_id,
                status=ValidationStatus.PASSED if is_passing_evaluation else ValidationStatus.FAILED,
                reason=evaluation_description,
            )
        )
