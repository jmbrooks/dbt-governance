from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from dbt_governance.structures.severity import Severity


class ValidationStatus(Enum):
    """Enumeration of possible statuses for a governance rule validation.

    Attributes:
        PASSED: The rule passed successfully.
        FAILED: The rule failed validation.
        ERROR: The rule could not be evaluated due to an issue.
        WARNING: The rule raised a non-critical concern.
    """

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    WARNING = "warning"

    def __repr__(self) -> str:
        """Return a user-friendly description of the validation status."""
        descriptions = {
            ValidationStatus.PASSED: "The rule passed successfully.",
            ValidationStatus.FAILED: "The rule failed validation.",
            ValidationStatus.ERROR: "The rule could not be evaluated due to an issue.",
            ValidationStatus.WARNING: "The rule raised a non-critical concern.",
        }
        return descriptions[self]


class ValidationResult(BaseModel):
    """Represents the result of evaluating a governance rule.

    Attributes:
        rule_name (str): The name of the rule being validated.
        rule_severity (Severity): The severity of the rule based on the validation status.
        dbt_project_path (str): The path to the dbt project directory.
        resource_type (str): The type of resource being validated (e.g., model, snapshot, source).
        unique_id (str): The unique identifier of the resource being validated (e.g. model.my_project.dim_date).
        status (ValidationStatus): The status of the rule validation, indicating whether it passed, failed, etc.
        reason (Optional[str]): An optional explanation for the validation status (e.g., why a rule failed or
            flagged a warning).
    """

    model_config = ConfigDict(use_enum_values=True)

    rule_name: str = Field(..., description="The name of the rule being validated.")
    dbt_project_path: str = Field(..., description="The path to the dbt project directory.")
    resource_type: str = Field(..., description="The type of resource being validated.")
    unique_id: str = Field(..., description="The unique identifier of the resource being validated.")
    status: ValidationStatus = Field(..., description="The status of the rule validation.")
    rule_severity: Severity = Field(
        default=Severity.default_rule_severity(), description="The severity of the rule based on the validation status"
    )
    reason: Optional[str] = Field(None, description="An optional explanation for the validation status.")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ValidationResult to a dictionary for JSON serialization."""
        return {
            "rule_name": self.rule_name,
            "rule_severity": self.rule_severity,  # Convert Enum to string
            "dbt_project_path": self.dbt_project_path,
            "resource_type": self.resource_type,
            "unique_id": self.unique_id,
            "status": str(self.status),  # Convert Enum to string
            "reason": self.reason,
        }
