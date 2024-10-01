import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from tests.test_helpers.file_utils import assert_file_content, load_resources_dir
from tests.test_helpers.runner import TestRunner, assert_cli_output


def test_init_success(
    tmp_path: Path,
    runner: TestRunner,
    monkeypatch: MonkeyPatch,
) -> None:
    """Tests aeternum build in the success case."""
    monkeypatch.chdir(tmp_path)
    valid_spec_file = load_resources_dir("references", "generated_spec.yaml")
    generated_file_name = "my-spec.yaml"
    generated_spec_full_path = Path(tmp_path, generated_file_name)

    result = runner.run_cli(
        [
            "init",
            "--file",
            generated_file_name,
            "--name",
            "Test-Project",
            "--repo-url",
            "https://github.com/some-user/my-test-project",
            "--version",
            "0.1.0",
            "--strict",
        ]
    )
    assert_cli_output(
        result,
        ["Project specification exported to file", str(generated_spec_full_path)],
    )
    assert (
        generated_spec_full_path.exists()
    ), f"File '{generated_file_name}' not created"
    assert_file_content(generated_spec_full_path, valid_spec_file)
