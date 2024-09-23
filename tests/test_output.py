from unittest.mock import MagicMock, Mock, patch

from pytest import MonkeyPatch

from aeternum.output import run_validation_command


@patch("subprocess.run")
def test_run_validation_command_success(
    mock_subproc_run: MagicMock,
    monkeypatch: MonkeyPatch,
) -> None:
    """Test command validation via subprocess run with failure."""
    successful_subprocess_exec = Mock()
    successful_subprocess_exec.configure_mock(
        **{"returncode": 0, "stdout.decode.return_value": "Ran step successfully"}
    )
    unsuccessful_subprocess_exec = Mock()
    unsuccessful_subprocess_exec.configure_mock(
        **{"returncode": 1, "stdout.decode.return_value": "Failed to run step"}
    )
    mock_subproc_run.side_effect = [successful_subprocess_exec]
    result = run_validation_command("some-valid-bin", "-v", "run")
    assert result


@patch("subprocess.run")
def test_run_validation_command_failure(
    mock_subproc_run: MagicMock,
    monkeypatch: MonkeyPatch,
) -> None:
    """Test command validation via subprocess run with failure."""
    unsuccessful_subprocess_exec = Mock()
    unsuccessful_subprocess_exec.configure_mock(
        **{"returncode": 1, "stdout.decode.return_value": "Failed to run step"}
    )
    mock_subproc_run.side_effect = [unsuccessful_subprocess_exec]
    result = run_validation_command("some-invalid-command")
    assert not result
