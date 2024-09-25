import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

from pytest import MonkeyPatch, raises
from pytest_mock import MockerFixture

from aeternum.command.doctor import (
    AeternumRequirement,
    ExpectedBinary,
    ExpectedFile,
    validate_requirements,
)
from tests.test_helpers.file_utils import load_resources_dir
from tests.test_helpers.runner import TestRunner, assert_cli_output


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

    unsuccessful_subprocess_exec = __new_mock_subprocess("git", 0, "true")
    mock_subproc_run.side_effect = [unsuccessful_subprocess_exec]

    result = runner.run_cli(["doctor"])
    assert_cli_output(result, ["All dependencies ready"])


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


@patch("subprocess.run")
def test_validate_requirements(mock_subproc_run: MagicMock):
    unsuccessful_subprocess_exec = __new_mock_subprocess("git", 0, "true")
    mock_subproc_run.side_effect = [unsuccessful_subprocess_exec]
    mock_requirements = [
        ExpectedFile(
            "Some file requirement",
            "Test will fail",
            "Create this file",
            "/some/valid/path",
        ),
        ExpectedBinary(
            "Some bin requirement",
            "Test will fail also",
            "Install this",
            "some-valid-bin",
        ),
    ]
    fixes_needed = validate_requirements(mock_requirements)
    assert (
        len(fixes_needed) == 1
    ), f"Expected 1 requirement should need fixing but found {len(fixes_needed)}"


def test_validate_requirements_invalid_input():
    mock_requirements = ["some requirement"]
    with raises(TypeError):
        _ = validate_requirements(mock_requirements)
