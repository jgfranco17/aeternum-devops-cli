import os
import tempfile
from typing import Dict

from behave.runner import Context

from tests.shared.runner import TestRunner


class AeternumContext(Context):
    """Custom Aeternum context type stub.

    AeternumContext extends Behave's dynamic Context class to include
    additional attributes used during BDD test execution.

    Primarily used for IDE support for type hints.

    Attributes:
        temp_dir (str): Temporary directory for testing
        runner (TestRunner): Test runner for executing CLI commands
    """

    cwd: str
    temp_dir: str
    environment_variables: Dict[str, str]
    runner: TestRunner
