from dbt_governance.structures.evaluation_status import EvaluationStatus


def test_evaluation_status_members() -> None:
    """Test that EvaluationStatus Enum members have the correct values."""
    assert EvaluationStatus.SUCCESS.value == "success"
    assert EvaluationStatus.INITIALIZATION.value == "initialization"
    assert EvaluationStatus.PENDING.value == "pending"
    assert EvaluationStatus.ERROR.value == "error"


def test_evaluation_status_exit_code() -> None:
    """Test the exit_code property of EvaluationStatus Enum."""
    assert EvaluationStatus.SUCCESS.exit_code == 0
    assert EvaluationStatus.INITIALIZATION.exit_code == 1
    assert EvaluationStatus.PENDING.exit_code == 1
    assert EvaluationStatus.ERROR.exit_code == 1


def test_evaluation_status_iteration() -> None:
    """Test that all members of EvaluationStatus can be iterated over."""
    statuses = list(EvaluationStatus)
    assert len(statuses) == 4
    assert EvaluationStatus.SUCCESS in statuses
    assert EvaluationStatus.INITIALIZATION in statuses
    assert EvaluationStatus.PENDING in statuses
    assert EvaluationStatus.ERROR in statuses
