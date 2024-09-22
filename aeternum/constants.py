from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ProjectFiles:
    """Constants for generated files."""

    SPEC_FILE: str = "specs.yaml"


@dataclass(frozen=True)
class ConsoleIcons:
    """Icons for the shell prints."""

    CHECK: str = "\u2713"
    CROSS: str = "\u2715"


class StepType(str, Enum):
    """Possible values for build steps."""

    BUILD: str = "build"
    TEST: str = "test"
    DEPLOY: str = "deploy"
