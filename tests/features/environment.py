import os
import shutil
import tempfile

from behave.runner import Context

from tests.shared.runner import TestRunner


def before_scenario(context: Context, scenario: object) -> None:
    """Switch to a temporary directory before each scenario."""
    context.cwd = os.getcwd()
    context.temp_dir = tempfile.mkdtemp(prefix="aeternum")
    context.runner = TestRunner()
    os.chdir(context.temp_dir)


def after_scenario(context: Context, scenario: object) -> None:
    """Reset to the original directory after each scenario."""
    os.chdir(context.cwd)
    shutil.rmtree(context.temp_dir)
