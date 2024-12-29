from pathlib import Path
from unittest.mock import MagicMock, patch

from dbt_governance.tasks.validate_config import validate_config_task


def test_validate_config_task_valid_file() -> None:
    """Test validate_config_task with a valid configuration file."""
    with patch("builtins.open", MagicMock(return_value=MagicMock())) as mock_open:
        with patch("yaml.safe_load", return_value={"dbt_cloud": {"api_token": "test_token"}}) as mock_safe_load:
            with patch(
                "dbt_governance.tasks.validate_config.validate_config_structure", return_value=[]
            ) as mock_validate_structure:
                is_valid, message = validate_config_task("valid_config.yml")

                # Assertions
                assert is_valid is True
                assert "Configuration file is valid!" in message
                mock_open.assert_called_once_with("valid_config.yml", "r")
                mock_safe_load.assert_called_once()
                mock_validate_structure.assert_called_once()


def test_validate_config_task_invalid_yaml() -> None:
    """Test validate_config_task with invalid YAML."""
    # with patch("builtins.open", MagicMock(return_value=MagicMock())) as mock_open:
    #     with patch("yaml.safe_load", side_effect=ValueError("mocked YAML error")) as mock_safe_load:
    invalid_config_file = Path("invalid_config.yml")
    invalid_config_file.touch()
    is_valid, message = validate_config_task(str(invalid_config_file))

    # Assertions
    assert is_valid is False
    assert "Failed to load configuration file: mocked YAML error" in message
            # mock_open.assert_called_once_with("invalid_config.yml", "r")
            # mock_safe_load.assert_called_once()


def test_validate_config_task_validation_errors() -> None:
    """Test validate_config_task with validation errors."""
    with patch("builtins.open", MagicMock(return_value=MagicMock())) as mock_open:
        with patch("yaml.safe_load", return_value={"dbt_cloud": {"api_token": "test_token"}}) as mock_safe_load:
            with patch(
                "dbt_governance.tasks.validate_config.validate_config_structure",
                return_value=["Missing required key: 'global_rules_file'", "Invalid dbt_cloud.organization_id"],
            ) as mock_validate_structure:
                is_valid, message = validate_config_task("config_with_errors.yml")

                # Assertions
                assert is_valid is True  # Validation errors do not make the config "invalid" outright
                assert "- Missing required key: 'global_rules_file'" in message
                assert "- Invalid dbt_cloud.organization_id" in message
                mock_open.assert_called_once_with("config_with_errors.yml", "r")
                mock_safe_load.assert_called_once()
                mock_validate_structure.assert_called_once()


def test_validate_config_task_exception() -> None:
    """Test validate_config_task with an exception when opening the file."""
    with patch("builtins.open", side_effect=FileNotFoundError("mocked file not found")) as mock_open:
        is_valid, message = validate_config_task("missing_config.yml")

        # Assertions
        assert is_valid is False
        assert "Failed to load configuration file: mocked file not found" in message
        mock_open.assert_called_once_with("missing_config.yml", "r")


def test_validate_config_task_redacted_config() -> None:
    """Test validate_config_task redacts sensitive keys in logs."""
    with patch("builtins.open", MagicMock(return_value=MagicMock())) as mock_open:
        with patch("yaml.safe_load", return_value={"dbt_cloud": {"api_token": "sensitive_token"}}) as mock_safe_load:
            with patch(
                "dbt_governance.tasks.validate_config.validate_config_structure", return_value=[]
            ) as mock_validate_structure:
                with patch("dbt_governance.tasks.validate_config.logger") as mock_logger:
                    is_valid, message = validate_config_task("config_with_sensitive_data.yml")

                    # Assertions
                    assert is_valid is True
                    assert "Configuration file is valid!" in message
                    mock_open.assert_called_once_with("config_with_sensitive_data.yml", "r")
                    mock_safe_load.assert_called_once()
                    mock_validate_structure.assert_called_once()
                    mock_logger.debug.assert_called_once()
                    redacted_config = mock_logger.debug.call_args[0][0]
                    assert "REDACTED" in redacted_config
