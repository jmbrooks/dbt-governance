from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

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

    def __str__(self):
        """Return the string representation for JSON serialization."""
        return self.value

    def __repr__(self) -> str:
        """Return a user-friendly description of the validation status."""
        descriptions = {
            ValidationStatus.PASSED: "The rule passed successfully.",
            ValidationStatus.FAILED: "The rule failed validation.",
            ValidationStatus.ERROR: "The rule could not be evaluated due to an issue.",
            ValidationStatus.WARNING: "The rule raised a non-critical concern.",
        }
        return descriptions[self]


@dataclass
class ValidationResult:
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

    rule_name: str
    rule_severity: Severity
    dbt_project_path: str
    resource_type: str
    unique_id: str
    status: ValidationStatus
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ValidationResult to a dictionary for JSON serialization."""
        return {
            "rule_name": self.rule_name,
            "rule_severity": str(self.rule_severity),  # Convert Enum to string
            "dbt_project_path": self.dbt_project_path,
            "resource_type": self.resource_type,
            "unique_id": self.unique_id,
            "status": str(self.status),  # Convert Enum to string
            "reason": self.reason,
        }
