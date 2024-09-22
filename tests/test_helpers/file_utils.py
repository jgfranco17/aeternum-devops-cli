import inspect
import os
from pathlib import Path
from typing import Any, List, Tuple, Union
from unittest.mock import MagicMock

from pytest_mock import MockerFixture


def assert_files_created(working_dir: Union[str, Path], files: List[str]) -> None:
    """Assert that the expected files to be generated are created."""
    for file in files:
        full_path = Path(os.path.join(working_dir, file))
        assert full_path.exists(), f"Templated file '{str(full_path)}' was not created"


def load_resources_dir(*filepath: Tuple[str]) -> Path:
    """Load a directory relative to the test package resources."""
    return Path(Path(__file__).parent.resolve(), "resources", *filepath)


def assert_files(test_file: str, reference_file: str) -> None:
    """Compare 2 file by asserting all lines.

    Args:
        test_file (str): generated file
        reference_file (str): reference to compare against

    Raises:
        AssertionError: if the generated file does not match the reference
    """
    # Confirm that the file exists
    assert os.path.exists(test_file), f"Test file does not exist: {test_file}"

    with open(test_file) as actual, open(reference_file) as reference:
        test_lines = actual.readlines()
        reference_lines = reference.readlines()

        # Verify that the two files are of equal length
        if len(reference_lines) != len(test_lines):
            raise AssertionError(
                f"{reference_file} has {len(reference_lines)} lines vs "
                + f"{test_file} has {len(test_lines)}; cannot compare!"
                + f"\n\n--- {reference_file} ---\n{''.join(reference_lines)}"
                + f"\n\n--- {test_file} ---\n{''.join(test_lines)}"
            )

        # Compare line by line
        for line_number, (ref, test) in enumerate(zip(reference_lines, test_lines)):
            if ref != test:
                print(
                    f"RTeference file: {reference_file} <==> Generated file {test_file}"
                )
                print(f"Not matching line {line_number} =>")
                print(f"  Ref: {ref}")
                print(f"  Gen: {test}")
