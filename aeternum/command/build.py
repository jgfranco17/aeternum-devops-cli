import logging
from pathlib import Path

import click

from aeternum.core.constants import ProjectFiles
from aeternum.core.errors import AeternumInputError
from aeternum.core.models import ProjectSpec

logger = logging.getLogger(__name__)


@click.command("build")
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="Path to YAML config file",
    default=ProjectFiles.SPEC_FILE,
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Get summary of build steps without running them.",
    default=False,
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="If passed, output from build steps will not be printed out.",
    default=False,
)
@click.option(
    "--save-output",
    is_flag=True,
    help="Save execution output to file.",
    default=False,
)
def build_project(file: str, dry_run: bool, quiet: bool, save_output: bool) -> None:
    """Initialize and build a project from specification file."""
    project = ProjectSpec.load_from_yaml(file)
    logger.info(f"Loaded project: {project.name} {project.version}")
    project.build_stage.validate(project.strict_build)
    project.build(dry_run, quiet, save_output)
