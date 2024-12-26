from enum import Enum


class Severity(Enum):
    """Enumeration of valid severities for governance rules.

    Attributes:
        CRITICAL: Failing this rule is of critical governance impact and should be addressed immediately.
        HIGH: Failing this rule is of high governance impact and should be addressed promptly.
        MEDIUM: Failing this rule is of medium governance impact and should be addressed in a timely manner.
        LOW: Failing this rule is of low governance impact and should be addressed as resources allow.
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @staticmethod
    def default_rule_severity() -> str:
        """Return the default severity for a governance rule."""
        return Severity.MEDIUM.value
