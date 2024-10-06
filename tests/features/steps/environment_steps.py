import os
from unittest.mock import MagicMock, call, patch

from behave import given, then

from tests.features.stubs import AeternumContext


@given('the variable "{env_variable:S}" is set to {value:S}')
def step_set_environment_variable(
    context: AeternumContext, env_variable: str, value: str
):
    """Set a temporary environment variable.

    Args:
        env_variable (str): Environment variable to manipulate
        value (str): Variable value to set
    """
    context.environment_variables.update({env_variable: os.getenv(env_variable)})
    os.environ[env_variable] = value
    print(f"Environment variable '{env_variable}' temporarily set.")


@given("subprocess calls are mocked")
def step_mock_subprocess(context: AeternumContext):
    # Create a MagicMock for subprocess.run and patch it
    context.mock_subprocess = MagicMock()
    context.mock_subprocess.return_value.returncode = 0
    context.mock_subprocess.return_value.stdout = "Mocked output"

    # Patch the subprocess.run with the MagicMock
    patch("subprocess.run", context.mock_subprocess).start()


@then("the subprocess was called")
def step_assert_subprocess_called(context: AeternumContext):
    assert context.mock_subprocess.called, "Missing subprocess.run call"
