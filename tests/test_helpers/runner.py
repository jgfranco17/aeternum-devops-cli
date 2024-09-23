from copy import deepcopy
from typing import List, Optional

from click.testing import CliRunner, Result

from aeternum.main import cli


class TestRunner:
    def __init__(self):
        self.env = {
            "GITHUB_USERNAME": "test-user",
            "GITHUB_API_TOKEN": "my-github-api-token",  # pragma: allowlist secret
        }
        self.__runner = CliRunner(mix_stderr=False)

    @property
    def directory(self) -> str:
        return self.__working_dir

    def run_cli(self, cli_args: List[str]) -> Result:
        """Run the Aeternum CLI with envs set."""
        env = deepcopy(self.env)
        return self.__runner.invoke(cli, ["-vv", *cli_args], env=env)


def assert_cli_output(
    result: Result,
    expected_stdout: List[str],
    expected_exit_code: Optional[int] = 0,
    expected_stderr: Optional[str] = "",
    expected_exception: Optional[SystemExit] = None,
) -> None:
    """Verify successful result, output and instantiated jama client."""
    # Will be captured by pytest most of the time.
    # By default it will only be shown if the test fails
    print("Actual stdout:")
    print(result.stdout)
    if expected_stdout:
        for output in expected_stdout:
            print(f"Expected stdout: {output}")
            assert output in result.stdout, "Expected stdout not found in actual stdout"
    print("Actual stderr:")
    print(result.stderr)
    if expected_stderr != "":
        print("Expected stderr:")
        print(expected_stderr)
        assert (
            expected_stderr in result.stderr
        ), "Expected error not found in actual stderr"

    assert (
        result.exit_code == expected_exit_code
    ), f"Expected exit code failed. Expected: {expected_exit_code}, Actual: {result.exit_code}"

    if expected_exception is None:
        assert (
            result.exception is expected_exception
        ), f"There was no exception expected but an exception was raised: {result.exception}"
    else:
        assert result.exception is not None
        assert isinstance(expected_exception, result.exception), (
            f"The expected exception type does not match the actual one.\n"
            + f"Expected: {type(expected_exception)}. Actual: {type(result.exception)}"
        )
        assert (
            type(result.exception) == SystemExit
        ), f"Only SystemExits are checked as expected exceptions! Found {type(result.exception)}"
        assert (
            result.exception.code == expected_exception.code
        ), f"""The expected exception code does not match the actual one.
        Expected: {expected_exception.code}. Actual: {result.exception.code}"""
