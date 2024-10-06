import os
from unittest.mock import patch

from behave import given, then, when

from tests.features.steps.utils import (
    find_captured_variables,
    get_successful_subprocess_mock,
)
from tests.features.stubs import AeternumContext


@given("I have the Aeternum CLI installed")
def step_verify_cli_installation(context: AeternumContext):
    """Check if the CLI tool is accessible."""
    result = context.runner.run_cli(["--version"])
    assert result.exit_code == 0, "Aeternum CLI is not installed or is inaccessible"


@given('the variable "{env_variable:S}" is set to {value:S}')
def step_set_environment_variable(
    context: AeternumContext, env_variable: str, value: str
):
    """_summary_

    Args:
        env_variable (str): Environment variable to manipulate
        value (str): Variable value to set
    """
    context.environment_variables.update({env_variable: os.getenv(env_variable)})
    os.environ[env_variable] = value


@when('I run "aeternum {command}"')
def step_run_cli_command(context: AeternumContext, command: str):
    """Run an Aeternum CLI command with.

    Performs variable substitution if any variables were captured prior.

    Args:
        command (str): Command string to execute
    """
    captured_variables = find_captured_variables(command)
    exec_command = command
    if captured_variables:
        for var in captured_variables:
            value = context.captured_variables.get(var, None)
            if value:
                exec_command = command.replace(f"$[{var}]", value)
                print(exec_command, f"$[{var}]", value, sep=" | ")
    context.result = context.runner.run_cli(exec_command.split())


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
