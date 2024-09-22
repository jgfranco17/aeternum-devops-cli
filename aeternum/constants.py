from dataclasses import dataclass
from enum import Enum
from typing import Final


@dataclass(frozen=True)
class ProjectFiles:
    """Constants for generated files."""

    SPEC_FILE: Final[str] = "aeternum.yaml"


@dataclass(frozen=True)
class StepExecutionStatus:
    """Constants for execution statuses."""

    COMPLETED: Final[str] = "COMPLETED"
    FAILED: Final[str] = "FAILED"
    SKIPPED: Final[str] = "SKIPPED"


@dataclass(frozen=True)
class ConsoleIcons:
    """Icons for the shell prints."""

    CHECK: Final[str] = "\u2713"
    CROSS: Final[str] = "\u2715"


class StepType(str, Enum):
    """Possible values for build steps."""

    BUILD: str = "build"
    TEST: str = "test"
    DEPLOY: str = "deploy"
