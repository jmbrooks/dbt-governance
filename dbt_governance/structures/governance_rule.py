from dataclasses import dataclass
from typing import Optional, List
from dbt_governance.structures.severity import Severity


@dataclass
class GovernanceRule:
    """Represents a governance rule to evaluate dbt projects."""
    name: str
    description: str
    severity: Severity
    paths: Optional[List[str]] = None  # Affected paths (e.g., folders/models)
    checks: Optional[dict] = None      # Specific check details (e.g., test types)
