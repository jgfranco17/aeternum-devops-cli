import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import click

from aeternum.core.constants import ConsoleIcons, ProjectFiles
from aeternum.core.output import run_validation_command

logger = logging.getLogger(__name__)


@dataclass
class AeternumRequirement:
    name: str
    impact_if_missing: str
    help_text: str


@dataclass
class ExpectedFile(AeternumRequirement):
    path_in_repo: str


@dataclass
class ExpectedBinary(AeternumRequirement):
    command: str
    args: Optional[List[str]] = None
    ready: bool = None

    def __post_init__(self) -> None:
        cmd_validation = None
        if self.args is None:
            cmd_validation = run_validation_command(self.command)
        else:
            cmd_validation = run_validation_command(self.command, *self.args)
        self.ready = cmd_validation


@click.command("doctor")
def doctor() -> None:
    """Validate current workspace for Aeternum CI compatibility."""
    required_bins = [
        ExpectedBinary(
            name="Git",
            command="git",
            args=["rev-parse", "--is-inside-work-tree"],
            impact_if_missing="Cannot perform build checks without a Git repository",
            help_text="Ensure you are re in a Git repository",
        ),
    ]
    required_files = [
        ExpectedFile(
            name="Aeternum YAML config file",
            path_in_repo=ProjectFiles.SPEC_FILE,
            impact_if_missing="Cannot build project without configuration file",
            help_text=f"Create an {ProjectFiles.SPEC_FILE} file in the root of your project directory",
        ),
    ]

    click.echo("Aeternum Doctor:")
    fixes_needed = validate_requirements([*required_bins, *required_files])
    click.echo("-" * 20)
    if fixes_needed:
        click.echo(f"Doctor found {len(fixes_needed)} fixes needed:")
        for fix in fixes_needed:
            click.secho(f"- {fix}", fg="yellow")
    else:
        click.echo(f"All dependencies ready!")


def validate_requirements(requirements: List[AeternumRequirement]) -> List[str]:
    fixes = []
    for req in requirements:
        ready_condition = None
        if isinstance(req, ExpectedFile):
            ready_condition = Path(req.path_in_repo).exists()
        elif isinstance(req, ExpectedBinary):
            ready_condition = req.ready
        else:
            raise TypeError(f"Unsupported requirement type: {type(req).__name__}")

        if not ready_condition:
            click.secho(
                f"[{ConsoleIcons.CROSS}] {req.name} missing: {req.impact_if_missing}",
                fg="red",
            )
            fixes.append(req.help_text)
        else:
            click.secho(f"[{ConsoleIcons.CHECK}] {req.name} ready", fg="green")

    logger.debug(
        f"Validated {len(requirements)} requirements, {len(fixes)} fixes needed"
    )
    return fixes
