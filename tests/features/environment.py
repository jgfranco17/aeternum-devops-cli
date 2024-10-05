import os
import shutil
import tempfile

from behave.runner import Context


def before_scenario(context: Context, scenario: object) -> None:
    """Switch to a temporary directory before each scenario."""
    context.temp_dir = tempfile.mkdtemp()
    context.cwd = os.getcwd()
    os.chdir(context.temp_dir)


def after_scenario(context: Context, scenario: object) -> None:
    """Reset to the original directory after each scenario."""
    os.chdir(context.cwd)
    shutil.rmtree(context.temp_dir)
