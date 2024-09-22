import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

from pytest import LogCaptureFixture, MonkeyPatch
from pytest_mock import MockerFixture

from tests.test_helpers.file_utils import load_resources_dir
from tests.test_helpers.runner import TestRunner


@patch("subprocess.run")
def test_build_success(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum doctor in the success case."""
    monkeypatch.chdir(tmp_path)
    valid_spec_file = load_resources_dir("valid", "aeternum.yaml")
    shutil.copy(valid_spec_file, Path(tmp_path, "aeternum.yaml"))

    successful_subprocess_exec = Mock()
    successful_subprocess_exec.configure_mock(
        **{"returncode": 0, "stdout.decode.return_value": "Ran step successfully"}
    )
    mock_subproc_run.side_effect = [
        successful_subprocess_exec,
        successful_subprocess_exec,
    ]
    result = runner.run_cli(["build"])
    assert result.exit_code == 0


@patch("subprocess.run")
def test_build_step_failure(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum doctor in the success case."""
    monkeypatch.chdir(tmp_path)
    valid_spec_file = load_resources_dir("valid", "aeternum.yaml")
    shutil.copy(valid_spec_file, Path(tmp_path, "aeternum.yaml"))

    successful_subprocess_exec = Mock()
    successful_subprocess_exec.configure_mock(
        **{"returncode": 0, "stdout.decode.return_value": "Ran step successfully"}
    )
    unsuccessful_subprocess_exec = Mock()
    unsuccessful_subprocess_exec.configure_mock(
        **{"returncode": 1, "stdout.decode.return_value": "Failed to run step"}
    )
    mock_subproc_run.side_effect = [
        successful_subprocess_exec,
        unsuccessful_subprocess_exec,
    ]
    result = runner.run_cli(["build"])
    assert result.exit_code == 1


@patch("subprocess.run")
def test_build_invalid_spec_file(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum doctor in the success case."""
    monkeypatch.chdir(tmp_path)
    valid_spec_file = load_resources_dir("invalid_files", "aeternum-no-tests.yaml")
    shutil.copy(valid_spec_file, Path(tmp_path, "aeternum.yaml"))

    result = runner.run_cli(["build"])
    assert result.exit_code == 2
    assert "No test steps found in test-project build stage" in result.stderr
