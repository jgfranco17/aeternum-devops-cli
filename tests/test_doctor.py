from unittest.mock import MagicMock, Mock, patch

from tests.test_helpers.runner import TestRunner


def __new_mock_subprocess(name: str) -> Mock:
    value = Mock()
    output = {"returncode": 0, "stdout.decode.return_value": f"{name} 1.2.3"}
    value.configure_mock(**output)
    return value


def __new_mock_subprocess_with_err(name: str, exit_code: int, output: str) -> Mock:
    value = Mock()
    output = {
        "returncode": exit_code,
        "stdout.decode.return_value": f"Some {name} error: {output}",
    }
    value.configure_mock(**output)
    return value


@patch("subprocess.run")
def test_doctor_success(
    mock_subproc_run: MagicMock,
    runner: TestRunner,
) -> None:
    result = runner.run_cli(["doctor"])
    assert result.exit_code == 0
