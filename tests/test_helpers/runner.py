from copy import deepcopy
from typing import List

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
