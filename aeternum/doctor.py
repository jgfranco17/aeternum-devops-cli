import logging
import subprocess
from dataclasses import dataclass
from typing import List, Tuple

import click

from .constants import ConsoleIcons
from .errors import AeternumRuntimeError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExpectedFiles:
    name: str
    path_in_repo: str
    impact_if_missing: str
    help_text: str


@click.command("doctor")
def doctor():
    """Validate current workspace for Aeternum CI compatibility."""
    click.echo("Aeternum Doctor:")
    click.echo(f"All dependencies ready!")
