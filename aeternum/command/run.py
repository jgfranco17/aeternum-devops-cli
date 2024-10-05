import logging
from typing import Optional, Tuple

import click

from aeternum.core.constants import ProjectFiles
from aeternum.core.errors import AeternumInputError
from aeternum.core.models import ProjectSpec

logger = logging.getLogger(__name__)


@click.command("run")
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
@click.option(
    "--include",
    multiple=True,
    required=False,
    help="Run only specific step types (e.g. 'build', 'test', or 'deploy').",
)
@click.option(
    "--exclude",
    multiple=True,
    required=False,
    help="Run only specific step types (e.g. 'build', 'test', or 'deploy').",
)
def run_scripts(
    file: str,
    dry_run: bool,
    quiet: bool,
    save_output: bool,
    include: Optional[Tuple[str, ...]],
    exclude: Optional[Tuple[str, ...]],
) -> None:
    """Initialize and build a project from specification file."""
    project = ProjectSpec.load_from_yaml(file)
    logger.info(f"Loaded project: {project.name} {project.version}")
    project.build_stage.validate(project.strict_build)
    common_step_types = list(set(include) & set(exclude))
    if len(common_step_types) > 0:
        raise AeternumInputError(
            message=f"Found {len(common_step_types)} overlaps in include "
            + "and exclude options.",
            help_text=f"Conflicting filters: {common_step_types}",
        )
    project.build(
        dry_run_mode=dry_run,
        quiet_output=quiet,
        export_logs=save_output,
        include_filters=include,
        exclude_filters=exclude,
    )
