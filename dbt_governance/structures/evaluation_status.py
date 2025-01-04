from enum import Enum


class EvaluationStatus(Enum):
    """Enumeration of valid evaluation run statuses.

    Attributes:
        INITIALIZATION: Evaluation run status is in the setup and initialization phase.
        PENDING: Evaluation run status is in progress, so its status is still pending.
        SUCCESS: The evaluation run completed successfully.
        ERROR: The evaluation run did not fully complete, so it is in an invalid error state.
    """

    SUCCESS = "success"
    INITIALIZATION = "initialization"
    PENDING = "pending"
    ERROR = "error"

    @property
    def exit_code(self) -> int:
        """Return associated exit code with the evaluation status, where 0 is a successful exit code."""
        return 0 if self == EvaluationStatus.SUCCESS else 1
