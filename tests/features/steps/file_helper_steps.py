import os
import shutil
from pathlib import Path

from behave import given, then

from tests.features.stubs import AeternumContext
from tests.shared.file_utils import load_resources_dir


@given('the file "{filename:S}" is present in the current directory')
def step_assert_file_exists(context: AeternumContext, filename: str):
    """Assert that the specified file exists.

    Args:
        filename (str): File path in directory
    """
    assert os.path.exists(context.temp_dir, filename), f"File {filename} does not exist"


@given('the file "{filename:S}" does not exist')
def step_assert_file_does_not_exist(context: AeternumContext, filename: str):
    """Assert that the specified file doesn't exist.

    Args:
        filename (str): File path in directory
    """
    assert os.path.exists(context.temp_dir, filename), f"File {filename} already exists"


@given('I create the file "{filename:S}" in the current directory')
def step_create_file(context: AeternumContext, filename: str):
    """Creates a temp test file in the current directory.

    Args:
        filename (str): File to create
    """
    test_file = Path(context.temp_dir, filename)
    assert not test_file.exists(), f"File {filename} already exists"
    test_file.touch()


@given('I have reference file "{filepath:S}" captured as "{variable:w}"')
def step_copy_reference_file(context: AeternumContext, filepath: str, variable: str):
    """Copies a reference file to the temp working directory.

    Args:
        filepath (str): Path to the reference file
        variable (str): Variable to capture the path
    """
    reference_file = load_resources_dir(*filepath.split(os.sep))
    assert (
        reference_file.exists() and reference_file.is_file()
    ), f"Reference file does not exist or not file: {reference_file}"
    shutil.copy(reference_file, context.temp_dir)
    context.captured_variables[variable] = str(reference_file)


@then('the file "{filename:S}" was created')
def step_check_file_exists(context: AeternumContext, filename: str):
    """Assert that the specified file was created by CLI command.

    Args:
        filename (str): _description_
    """
    assert os.path.exists(filename), f"File {filename} does not exist"
