import os
import subprocess
from pathlib import Path

from behave import given, then, when
from behave.runner import Context


@given("I have the Aeternum CLI installed")
def step_verify_cli_installation(context: Context):
    # Check if the CLI tool is accessible
    result = subprocess.run(["aeternum", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "Aeternum CLI is not installed or is inaccessible."


@given('the file "{filename:S}" is present in the current directory')
def step_verify_cli_installation(context: Context, filename: str):
    assert os.path.exists(context.temp_dir, filename), f"File {filename} does not exist"


@given('I create the file "{filename:S}" in the current directory')
def step_verify_cli_installation(context: Context, filename: str):
    test_file = Path(context.temp_dir, filename)
    assert not test_file.exists(), f"File {filename} already exists"
    test_file.touch()


@given('the file "{filename:S}" does not exist')
def step_verify_cli_installation(context: Context, filename: str):
    assert os.path.exists(context.temp_dir, filename), f"File {filename} already exists"


@when('I run "{command}"')
def step_run_cli_command(context: Context, command: str):
    context.result = subprocess.run(command.split(), capture_output=True, text=True)


@then('the stdout should contain "{expected_output}"')
def step_impl(context: Context, expected_output: str):
    assert (
        expected_output in context.result.stdout
    ), f"Expected output to contain {expected_output}"


@then('the stderr should contain "{expected_err}"')
def step_impl(context: Context, expected_err: str):
    assert (
        expected_err in context.result.stderr
    ), f"Expected output to contain {expected_err}"


@then("the CLI should return exit code {expected_exit_code:d}")
def step_impl(context: Context, expected_exit_code: int):
    assert (
        context.result.returncode == expected_exit_code
    ), f"Expected exit code {expected_exit_code}, but got {context.result.returncode}"


@then('the file "{filename:S}" was created')
def step_check_file_exists(context: Context, filename: str):
    assert os.path.exists(filename), f"File {filename} does not exist"


@then("the file content should match:")
def step_assert_file_content_matches(context: Context):
    expected_content = context.text.strip()
    with open(context.filename) as file:
        actual_content = file.read().strip()
    assert actual_content == expected_content, "File content does not match"
