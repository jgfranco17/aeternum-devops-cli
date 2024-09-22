import os
from pathlib import Path
from typing import Tuple, Union


def assert_files_created(working_dir: Union[str, Path], *files: Tuple[str]) -> None:
    """Assert that the expected files to be generated are created."""
    file_contents = list(
        map(lambda s: f"- {s.relative_to(working_dir)}", Path(working_dir).iterdir())
    )
    contents_list = "\n".join(file_contents)
    for file in files:
        full_path = Path(os.path.join(working_dir, file))
        assert (
            full_path.exists()
        ), f"File '{file}' not created.\nFound {len(file_contents)} files:\n{contents_list}"


def load_resources_dir(*filepath: Tuple[str]) -> Path:
    """Load a directory relative to the test package resources."""
    return Path(Path(__file__).parent.resolve(), "resources", *filepath)


def assert_file_content(test_file: Path, reference_file: Path) -> None:
    """Compare 2 file by asserting all lines.

    Args:
        test_file (Path): generated file
        reference_file (Path): reference to compare against

    Raises:
        AssertionError: if the generated file does not match the reference
    """
    # Confirm that the file exists
    assert os.path.exists(test_file), f"Test file does not exist: {test_file}"

    with open(test_file) as actual, open(reference_file) as reference:
        test_lines = actual.readlines()
        ref_lines = reference.readlines()

    # Verify that the two files are of equal length
    if len(ref_lines) != len(test_lines):
        raise AssertionError(
            f"{reference_file} has {len(ref_lines)} lines vs "
            + f"{test_file} has {len(test_lines)}; cannot compare!"
            + f"\n\n--- {reference_file} ---\n{''.join(ref_lines)}"
            + f"\n\n--- {test_file} ---\n{''.join(test_lines)}"
        )

    # Compare line by line
    for idx, (ref, test) in enumerate(zip(ref_lines, test_lines), start=1):
        assert ref == test, (
            f"Reference file: {reference_file} <==> Generated file {test_file}, "
            + f"mismatch on line {idx}\n\n"
            + f"  Ref: {ref}\n"
            + f"  Gen: {test}\n"
        )
