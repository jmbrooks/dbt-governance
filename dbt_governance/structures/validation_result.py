from dataclasses import dataclass
from typing import Optional
from enum import Enum


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

    def __str__(self) -> str:
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
        status (ValidationStatus): The status of the rule validation, indicating whether it passed, failed, etc.
        reason (Optional[str]): An optional explanation for the validation status (e.g., why a rule failed or
            flagged a warning).
    """
    rule_name: str
    status: ValidationStatus
    reason: Optional[str] = None
