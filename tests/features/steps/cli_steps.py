import os
from pathlib import Path

from behave import given, then, when

from tests.features.stubs import AeternumContext


@given("I have the Aeternum CLI installed")
def step_verify_cli_installation(context: AeternumContext):
    """Check if the CLI tool is accessible."""
    result = context.runner.run_cli(["--version"])
    assert result.exit_code == 0, "Aeternum CLI is not installed or is inaccessible"


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


@when('I run "aeternum {command}"')
def step_run_cli_command(context: AeternumContext, command: str):
    """Run an Aeternum CLI command.

    Args:
        command (str): Command string to execute
    """
    context.result = context.runner.run_cli(command.split())


@then('the stdout should contain "{expected_output}"')
def step_impl(context: AeternumContext, expected_output: str):
    """Verfiy that the stdout contains the expected output.

    Args:
        expected_output (str): Substring line to look for in stdout
    """
    assert (
        expected_output in context.result.stdout
    ), f"Expected output to contain {expected_output}"


@then('the stderr should contain "{expected_err}"')
def step_impl(context: AeternumContext, expected_err: str):
    """Verfiy that the stderr contains the expected error message.

    Args:
        expected_err (str): Substring line to look for in stderr
    """
    assert (
        expected_err in context.result.stderr
    ), f"Expected output to contain {expected_err}"


@then("the CLI should return exit code {expected_exit_code:d}")
def step_impl(context: AeternumContext, expected_exit_code: int):
    """Assert that the CLI returned the expected exit code.

    Args:
        expected_exit_code (int): Expected exit code
    """
    assert (
        context.result.exit_code == expected_exit_code
    ), f"Expected exit code {expected_exit_code}, but got {context.result.exit_code}"


@then('the file "{filename:S}" was created')
def step_check_file_exists(context: AeternumContext, filename: str):
    """Assert that the specified file was created by CLI command.

    Args:
        filename (str): _description_
    """
    assert os.path.exists(filename), f"File {filename} does not exist"
