import logging
import os
from pathlib import Path
from typing import List

import click

from aeternum.constants import ProjectFiles
from aeternum.errors import AeternumInputError
from aeternum.models import ProjectSpec

logger = logging.getLogger(__name__)


@click.command("build")
@click.option(
    "--file",
    "-f",
    type=Path,
    help="Path to spec file",
    default=ProjectFiles.SPEC_FILE,
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="If passed, output from build steps will not be printed out",
    default=False,
)
def build_project(file: str, quiet: bool) -> None:
    """Initialize and build a project from specification file."""
    project = ProjectSpec.load_from_yaml(file)
    logger.info(f"Loaded project: {project.name}")
    if project.strict_build:
        validation_result = project.build_stage.validate()
        if validation_result.test_step_count == 0:
            raise AeternumInputError(
                f"No test steps found in {project.name} build stage"
            )

    project.build(quiet)
