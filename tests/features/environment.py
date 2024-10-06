import os
import shutil
import tempfile
from unittest.mock import patch

from tests.features.stubs import AeternumContext
from tests.shared.runner import TestRunner


def before_all(context: AeternumContext) -> None:
    """Configure all common fixtures."""
    context.runner = TestRunner()
    context.environment_variables = dict()
    context.captured_variables = dict()
    print("Ready to run Aeternum feature tests!")


def before_scenario(context: AeternumContext, scenario: object) -> None:
    """Switch to a temporary directory before each scenario."""
    context.captured_variables = dict()
    context.cwd = os.getcwd()
    context.temp_dir = tempfile.mkdtemp(prefix="aeternum")
    os.chdir(context.temp_dir)


def after_scenario(context: AeternumContext, scenario: object) -> None:
    """Reset to the original directory after each scenario."""
    os.chdir(context.cwd)
    shutil.rmtree(context.temp_dir)
    if hasattr(context, "mock_subprocess"):
        patch.stopall()  # This will stop all active patches
    for variable, original_value in context.environment_variables.items():
        os.environ[variable] = original_value
