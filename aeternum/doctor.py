import logging
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import click

from .constants import ConsoleIcons, ProjectFiles

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AeternumRequirement:
    name: str
    impact_if_missing: str
    help_text: str


@dataclass(frozen=True)
class ExpectedFile(AeternumRequirement):
    path_in_repo: str


@click.command("doctor")
def doctor() -> None:
    """Validate current workspace for Aeternum CI compatibility."""
    required_files = [
        ExpectedFile(
            name="Git repo",
            path_in_repo=".git",
            impact_if_missing="Cannot integrate with Github workflows",
            help_text=f"Run 'git init' in your project directory",
        ),
        ExpectedFile(
            name="Aeternum YAML config file",
            path_in_repo=ProjectFiles.SPEC_FILE,
            impact_if_missing="Cannot build project without configuration file",
            help_text=f"Create an {ProjectFiles.SPEC_FILE} file in the root of your project directory",
        ),
    ]
    fixes_needed = []
    click.echo("Aeternum Doctor:")
    for file in required_files:
        if not Path(file.path_in_repo).exists():
            click.secho(
                f"[{ConsoleIcons.CROSS}] {file.name} not found: {file.impact_if_missing}",
                fg="red",
            )
            fixes_needed.append(file.help_text)
        else:
            click.secho(f"[{ConsoleIcons.CHECK}] {file.name} ready", fg="green")

    click.echo("-" * 20)
    if fixes_needed:
        click.echo(f"Doctor found {len(fixes_needed)} fixes needed:")
        for fix in fixes_needed:
            click.secho(f"- {fix}", fg="yellow")
    else:
        click.echo(f"All dependencies ready!")
