import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import click
import yaml
from pydantic import BaseModel, Field, ValidationError

from .constants import ProjectFiles, StepType
from .errors import AeternumInputError, AeternumRuntimeError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StepExecutionResult:
    stdout: str
    stderr: str
    exit_code: int


class AutomationStep(BaseModel):
    name: str
    type: StepType
    shell: Optional[str] = Field("/bin/bash")
    command: str
    args: Optional[List[str]] = None

    def run(self) -> StepExecutionResult:
        """Run the build commands with a specified shell."""
        cmd_exec = (
            self.command if not self.args else f"{self.command} {' '.join(self.args)}"
        )
        full_cmd = [self.shell, "-c", cmd_exec]
        click.echo(f"Executing command: '{cmd_exec}'")
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        return StepExecutionResult(
            stdout=result.stdout, stderr=result.stderr, exit_code=result.returncode
        )


class AutomationStrategy(BaseModel):
    strict: bool = Field(True)


class ValidationResult(BaseModel):
    build_step_count: int
    test_step_count: int
    deploy_step_count: int
    invalid_step_count: int

    def is_valid(self) -> bool:
        return self.invalid_step_count == 0


class BuildStage(BaseModel):
    strategy: AutomationStrategy
    steps: List[AutomationStep]

    def validate(self) -> ValidationResult:
        """Validate the build stage steps list.

        Returns:
            ValidationResult: Object with counts of build, test, and deploy steps.
        """
        build_count = 0
        test_count = 0
        deploy_count = 0
        invalid_count = 0
        for step in self.steps:
            match step.type:
                case StepType.BUILD:
                    build_count += 1
                case StepType.TEST:
                    test_count += 1
                case StepType.DEPLOY:
                    deploy_count += 1
                case _:
                    invalid_count += 1
                    click.echo(f"Unknown step type: {step.type}", err=True)

        return ValidationResult(
            build_step_count=build_count,
            test_step_count=test_count,
            deploy_step_count=deploy_count,
            invalid_step_count=invalid_count,
        )


class ProjectSpec(BaseModel):
    name: str
    repo_url: str = Field(..., alias="repo-url")
    version: str
    build_stage: BuildStage = Field(..., alias="build-stage")

    @property
    def strict_build(self) -> bool:
        """Get project build strategy strictness.

        Returns:
            bool: True if strict build strategy is enabled
        """
        return self.build_stage.strategy.strict

    def get_default_spec_path(self) -> Path:
        return Path(ProjectFiles.AETERNUM_CONFIG_DIR, ProjectFiles.SPEC_FILE)

    @classmethod
    def load_from_yaml(cls, filepath: Path) -> "ProjectSpec":
        """Build a ProjectSpec from a YAML file."""
        try:
            data = None
            full_filepath = Path(os.getcwd(), filepath)
            with open(full_filepath, "r") as file:
                data = yaml.safe_load(file)

            project = ProjectSpec(**data)
            click.echo(f"Loaded project: {project.name} v{project.version}")
            return project

        except FileNotFoundError:
            raise AeternumInputError(f"Project spec file not found: {full_filepath}")

        except (ValidationError, yaml.YAMLError) as e:
            raise AeternumInputError(
                f"Failed to load project spec from {filepath}"
            ) from e

    def build(self, quiet: bool) -> None:
        """Run the build steps for the project.

        Args:
            quiet (bool): If True, output from build steps will be suppressed.

        Raises:
            AeternumRuntimeError: If any build step fails
        """
        build_label = f"Building {self.name} v{self.version}"
        fill_char = click.style("=", fg="green")
        empty_char = click.style("-", fg="white", dim=True)
        build_progress = click.progressbar(
            iterable=self.build_stage.steps,
            label=build_label,
            fill_char=fill_char,
            empty_char=empty_char,
        )

        logger.info(f"Building project: {self.name}")
        with build_progress as builds:
            for idx, step in enumerate(builds, start=1):
                click.echo(
                    f"\n[{idx} / {len(self.build_stage.steps)}][{step.type.upper()}]: {step.name}"
                )
                result = step.run()
                if result.exit_code != 0:
                    raise AeternumRuntimeError(
                        f"Step '{step.name}' failed with exit code {result.exit_code}:"
                        + f"\n{result.stderr}"
                    )
                if not quiet:
                    click.echo(result.stdout)
                builds.update(1)
