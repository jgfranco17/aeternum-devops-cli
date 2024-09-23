import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from tests.test_helpers.file_utils import (
    assert_file_content,
    assert_files_created,
    load_resources_dir,
)
from tests.test_helpers.runner import TestRunner


@patch("subprocess.run")
def test_build_success(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum build in the success case."""
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
    assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
    assert (
        "Build completed for test-project v0.1.0" in result.output
    ), "Build completion not reported"
    assert (
        "Ran 2 automation steps" in result.output
    ), "Automation steps count not reported"


@patch("subprocess.run")
def test_build_step_failure(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum build in the failure case."""
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
    assert result.exit_code == 1, f"Expected exit code 1, got {result.exit_code}"
    assert "FAILED" in result.output, "Summary table did not appear in output"


@patch("subprocess.run")
def test_build_invalid_spec_file(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    mocker: MockerFixture,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum build in the success case."""
    monkeypatch.chdir(tmp_path)
    valid_spec_file = load_resources_dir("invalid_files", "aeternum-no-tests.yaml")
    shutil.copy(valid_spec_file, Path(tmp_path, "aeternum.yaml"))

    result = runner.run_cli(["build"])
    assert result.exit_code == 2, f"Expected exit code 2, got {result.exit_code}"
    assert "No test steps found in test-project build stage" in result.stderr


@patch("subprocess.run")
def test_build_with_log_output_all_steps_completed(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
    mock_datetime: MagicMock,
    mock_perf_counter: MagicMock,
) -> None:
    """Tests aeternum build with logs in the success case."""
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
    mock_perf_counter.side_effect = [0.0, 0.5]
    fixed_timestamp = "2024-08-01_12-34-56"
    mock_datetime_instance = MagicMock()
    mock_datetime_instance.strftime.return_value = fixed_timestamp
    mock_datetime.now.return_value = mock_datetime_instance

    result = runner.run_cli(["build", "--save-output"])
    assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
    expected_log_filename = "aeternum-execution_2024-08-01_12-34-56.log"
    generated_log_file = Path(tmp_path, expected_log_filename)
    assert_files_created(tmp_path, expected_log_filename)
    ref_log_file = load_resources_dir("references", "successful_output.log")
    assert_file_content(generated_log_file, ref_log_file)


@patch("subprocess.run")
def test_build_with_log_output_with_failing_step(
    mock_subproc_run: MagicMock,
    tmp_path: Path,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
    mock_datetime: MagicMock,
    mock_perf_counter: MagicMock,
) -> None:
    """Tests aeternum build with logs but steps fail."""
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
    mock_perf_counter.side_effect = [0.0, 0.5]
    fixed_timestamp = "2024-08-01_12-34-56"
    mock_datetime_instance = MagicMock()
    mock_datetime_instance.strftime.return_value = fixed_timestamp
    mock_datetime.now.return_value = mock_datetime_instance

    result = runner.run_cli(["build", "--save-output"])
    assert result.exit_code == 1, f"Expected exit code 1, got {result.exit_code}"
    expected_log_filename = "aeternum-execution_2024-08-01_12-34-56.log"
    generated_log_file = Path(tmp_path, expected_log_filename)
    assert_files_created(tmp_path, expected_log_filename)
    ref_log_file = load_resources_dir("references", "failed_step.log")
    assert_file_content(generated_log_file, ref_log_file)
