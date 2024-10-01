import logging
from pathlib import Path
from typing import List

import click
from pydantic import ValidationError

from aeternum.core.constants import ProjectFiles
from aeternum.core.models import ProjectSpec

logger = logging.getLogger(__name__)


@click.command("init")
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=False, path_type=Path),
    help="Path to YAML config file",
    default=ProjectFiles.SPEC_FILE,
)
@click.option(
    "--name",
    type=str,
    required=True,
    help="Name of the project.",
    prompt="Name of the project",
)
@click.option(
    "--repo-url",
    type=str,
    required=True,
    help="Repository URL of the project.",
    prompt="Repository URL of the project",
)
@click.option(
    "--version",
    type=str,
    required=True,
    help="Version of the project.",
    prompt="Project version",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Set project to strict strategy.",
    default=False,
)
def init_new_project(
    file: Path, name: str, repo_url: str, version: str, strict: bool
) -> None:
    """Initialize and build a project from specification file."""
    project_spec = ProjectSpec.load_from_inputs(
        name=name, repo_url=repo_url, version=version, strict=strict
    )
    project_spec.write(filepath=file)
