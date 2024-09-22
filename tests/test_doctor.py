import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

from pytest import LogCaptureFixture, MonkeyPatch
from pytest_mock import MockerFixture

from tests.test_helpers.file_utils import load_resources_dir
from tests.test_helpers.runner import TestRunner


def __new_mock_subprocess(name: str, exit_code: int, output: str) -> Mock:
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
    tmp_path: Path,
    mocker: MockerFixture,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum doctor in the success case."""
    monkeypatch.chdir(tmp_path)
    valid_spec_file = load_resources_dir("valid", "aeternum.yaml")
    shutil.copy(valid_spec_file, Path(tmp_path, "aeternum.yaml"))
    os.makedirs(Path(tmp_path, ".git"))

    result = runner.run_cli(["doctor"])
    assert result.exit_code == 0


@patch("subprocess.run")
def test_doctor_missing_requirements(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum doctor in the success case."""
    monkeypatch.chdir(tmp_path)
    result = runner.run_cli(["doctor"])
    assert result.exit_code == 0
    assert "Doctor found 2 fixes needed"
    assert "Git repo not found"
    assert "Aeternum YAML config file not found"


@patch("subprocess.run")
def test_doctor_no_test_steps_when_strict(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum doctor in the success case."""
    monkeypatch.chdir(tmp_path)
    valid_spec_file = load_resources_dir("invalid_files", "aeternum-no-tests.yaml")
    shutil.copy(valid_spec_file, Path(tmp_path, "aeternum-no-tests.yaml"))
    os.makedirs(Path(tmp_path, ".git"))

    result = runner.run_cli(["doctor"])
    assert result.exit_code == 0
    assert "Doctor found 2 fixes needed"
    assert "Git repo not found"
    assert "Aeternum YAML config file not found"
