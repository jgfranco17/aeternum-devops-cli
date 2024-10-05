import os
from pathlib import Path

from behave import given, then

from tests.features.stubs import AeternumContext


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


@given('I have reference file "{filename:S}" in the current directory')
def step_create_file(context: AeternumContext, filename: str):
    """Creates a temp test file in the current directory.

    Args:
        filename (str): File to create
    """
    test_file = Path(context.temp_dir, filename)
    assert not test_file.exists(), f"File {filename} already exists"
    test_file.touch()


@then('the file "{filename:S}" was created')
def step_check_file_exists(context: AeternumContext, filename: str):
    """Assert that the specified file was created by CLI command.

    Args:
        filename (str): _description_
    """
    assert os.path.exists(filename), f"File {filename} does not exist"
