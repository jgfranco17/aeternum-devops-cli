import datetime as dt
import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import List, Optional, Tuple

import click
import yaml
from colorama import Fore, Style
from pydantic import BaseModel, Field, ValidationError, field_validator
from tabulate import tabulate

from aeternum.core.constants import StepExecutionStatus, StepType
from aeternum.core.errors import (
    AeternumInputError,
    AeternumRuntimeError,
    AeternumValidationError,
)
from aeternum.core.output import get_command_string
from aeternum.core.writer import OrderedDumper

logger = logging.getLogger(__name__)


ALLOWED_STEP_TYPES: List[str] = [StepType.BUILD, StepType.TEST, StepType.DEPLOY]


@dataclass(frozen=True)
class StepExecutionResult:
    name: str
    command_executed: str
    stdout: str
    stderr: str
    exit_code: int


class AutomationStep(BaseModel):
    name: str
    category: str
    command: str
    working_dir: Optional[Path] = Field(os.path.relpath(str(Path.cwd()), os.getcwd()))
    args: Optional[List[str]] = []

    @field_validator("category")
    def validate_category(cls, v: str) -> str:
        valid_step_types = ALLOWED_STEP_TYPES
        if v not in valid_step_types:
            raise AeternumValidationError(
                f"Invalid category '{v}', must be one of: {valid_step_types}."
            )
        return v

    @field_validator("working_dir")
    def validate_working_directory(cls, dir_path: str) -> Path:
        working_dir_path = Path(dir_path)
        if not working_dir_path.exists():
            raise AeternumInputError(
                f"Working directory provided does not exist: {dir_path}",
                "Create the directory first, either manually or by a prior step.",
            )
        if not working_dir_path.is_dir():
            raise AeternumValidationError(f"Given path is not a directory: {dir_path}")
        return working_dir_path

    def run(self, shell: str) -> StepExecutionResult:
        """Run the build commands with a specified shell."""

        cmd_exec = get_command_string(self.command, self.args)
        full_cmd = [shell, "-c", cmd_exec]
        click.echo(f"Executing command: '{cmd_exec}'")
        result = subprocess.run(
            full_cmd, capture_output=True, text=True, cwd=self.working_dir
        )
        return StepExecutionResult(
            name=self.name,
            command_executed=cmd_exec,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )

    def should_run(self, includes: Tuple[str, ...], excludes: Tuple[str, ...]) -> bool:
        if includes and self.category not in includes:
            return False
        if excludes and self.category in excludes:
            return False
        return True


class AutomationStrategy(BaseModel):
    strict: bool = Field(True)
    shell: Optional[str] = Field("/bin/bash")


class ValidationSummary(BaseModel):
    build_step_count: int
    test_step_count: int
    deploy_step_count: int
    invalid_step_count: int

    def is_valid(self) -> bool:
        return self.invalid_step_count == 0


class BuildStage(BaseModel):
    strategy: AutomationStrategy
    steps: List[AutomationStep]

    def validate(self, strict: Optional[bool] = False) -> ValidationSummary:
        """Validate the build stage steps list.

        Returns:
            ValidationSummary: Object with counts of build, test, and deploy steps.
        """
        build_count = 0
        test_count = 0
        deploy_count = 0
        invalid_count = 0
        for step in self.steps:
            match step.category:
                case StepType.BUILD:
                    build_count += 1
                case StepType.TEST:
                    test_count += 1
                case StepType.DEPLOY:
                    deploy_count += 1

        if strict and test_count == 0:
            raise AeternumInputError("No test steps found in build stage")

        return ValidationSummary(
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

    class Config:
        populate_by_name: bool = True
        use_enum_values: bool = True

    @property
    def strict_build(self) -> bool:
        """Get project build strategy strictness.

        Returns:
            bool: True if strict build strategy is enabled
        """
        return self.build_stage.strategy.strict

    @property
    def shell(self) -> str:
        """Get build-strategy shell to use for executing steps.

        Returns:
            str: Shell path
        """
        return self.build_stage.strategy.shell

    @classmethod
    def load_from_inputs(
        cls, name: str, repo_url: str, version: str, strict: bool
    ) -> "ProjectSpec":
        """Build a ProjectSpec from inputs.

        Args:
            name (str): Project name
            repo_url (str): Online repository URL
            version (str): Semver version of project
            strict (bool): If True, project spec must contain test steps

        Returns:
            ProjectSpec: Project manifest
        """
        default_steps = [
            AutomationStep(
                name=f"Step {idx}",
                category=category,
                command="some-command",
                args=[],
            )
            for idx, category in enumerate(
                [StepType.BUILD, StepType.TEST, StepType.DEPLOY], start=1
            )
        ]
        build_stage_config = BuildStage(
            strategy=AutomationStrategy(strict=strict), steps=default_steps
        )

        return ProjectSpec(
            name=name,
            repo_url=repo_url,
            version=version,
            build_stage=build_stage_config,
        )

    def write(self, filepath: Path) -> None:
        """Write project specification to file.

        Args:
            filepath (Path): Output path to write to
        """
        full_filepath = filepath.with_suffix(".yaml").resolve()
        with open(full_filepath, "w") as file:
            yaml.dump(
                self.model_dump(),
                file,
                Dumper=OrderedDumper,
                sort_keys=False,
                indent=2,
                default_flow_style=False,
            )
        click.echo(f"Project specification exported to file: '{full_filepath}'")

    @classmethod
    def load_from_yaml(cls, filepath: Path) -> "ProjectSpec":
        """Build a ProjectSpec from a YAML file.

        Args:
            filepath (Path): Path of file to read from
        """
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

    def __create_log_output(
        self, steps: List[AutomationStep], duration: float, dry_run_mode: bool
    ):
        """Write execution log to file.

        Args:
            steps (List[AutomationStep]):
            duration (float): Total dura

        Args:
            steps (List[AutomationStep]): Automation steps executed
            duration (float): Total execution duration
            dry_run_mode (bool): Whether the execution was run in dry-run mode
        """
        timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"aeternum-execution_{timestamp}"
        output_file = Path(file_name).with_suffix(".log")
        mode = "DRY RUN" if dry_run_mode else "STANDARD"
        log_summary_rows = []
        step_counts_by_status = {}
        if not dry_run_mode:
            step_counts_by_status.update(
                {
                    StepExecutionStatus.COMPLETED: 0,
                    StepExecutionStatus.FAILED: 0,
                    StepExecutionStatus.SKIPPED: 0,
                }
            )
        else:
            step_counts_by_status.update(
                {
                    StepExecutionStatus.NOT_EXECUTED: 0,
                }
            )
        for idx, (step, status) in enumerate(steps, start=1):
            command = (
                step.command
                if not step.args
                else f"{step.command} {' '.join(step.args)}"
            )
            log_summary_rows.append([idx, step.name, command, status])
            step_counts_by_status[status] += 1

        log_summary_headers = ["#", "NAME", "COMMAND", "STATUS"]
        step_summary_report = tabulate(
            log_summary_rows,
            headers=log_summary_headers,
            showindex=False,
            numalign="center",
            tablefmt="simple",
        )
        with open(str(output_file.resolve()), "w") as file:
            file.write(f"Project: {self.name}\n")
            file.write(f"Version: {self.version}\n")
            file.write(f"Shell: {self.shell}\n")
            file.write(f"Execution duration: {duration:.3f}s\n\n")
            file.write("Step Summary:\n")
            for status, count in step_counts_by_status.items():
                file.write(f"{status}: {count}\n")
            file.write("\n")
            file.write(f"Build Output ({mode}):\n")
            file.write(step_summary_report)
            file.write("\n")

    def build(
        self,
        dry_run_mode: bool,
        quiet_output: bool,
        export_logs: bool,
        include_filters: Tuple[str, ...],
        exclude_filters: Tuple[str, ...],
    ) -> None:
        """Run the Aeternum steps for the project.

        Args:
            dry_run_mode (bool): If true, summarize the steps without executing
            quiet_output (bool): If true, output will not be printed to stdout
            export_logs (bool): If true, export the outputs as a log file
            include_filters (Tuple[str, ...]): Steps to include
            exclude_filters (Tuple[str, ...]): Steps to exclude

        Raises:
            AeternumRuntimeError: If any build steps fail
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
        executed_steps = []
        summary = []
        failed_step = None
        execution_start_time = perf_counter()
        with build_progress as builds:
            for idx, step in enumerate(builds, start=1):
                click.echo(
                    f"\n[{idx} / {len(self.build_stage.steps)}][{step.category.upper()}]: {step.name}"
                )
                if step.should_run(include_filters, exclude_filters):
                    if not dry_run_mode:
                        result = step.run(self.shell)
                        if result.exit_code != 0:
                            icon = f"{Fore.RED}{Style.BRIGHT}{StepExecutionStatus.FAILED}{Style.RESET_ALL}"
                            summary.append([idx, step.name, icon])
                            executed_steps.append((step, StepExecutionStatus.FAILED))
                            failed_step = result
                            break
                        if not quiet_output:
                            click.echo(result.stdout)

                        icon = f"{Fore.GREEN}{Style.BRIGHT}{StepExecutionStatus.COMPLETED}{Style.RESET_ALL}"
                        summary.append([idx, step.name, result.command_executed, icon])
                        executed_steps.append((step, StepExecutionStatus.COMPLETED))
                    else:
                        icon = f"{Fore.LIGHTBLACK_EX}{StepExecutionStatus.NOT_EXECUTED}{Style.RESET_ALL}"
                        summary.append(
                            [
                                idx,
                                step.name,
                                get_command_string(step.command, step.args),
                                icon,
                            ]
                        )
                        executed_steps.append((step, StepExecutionStatus.NOT_EXECUTED))

                else:
                    logger.debug(f"Step #{idx} filtered out, skipping execution")
                    executed_steps.append((step, StepExecutionStatus.EXCLUDED))

                # Update progress bar
                builds.update(1)

        execution_end_time = perf_counter()
        execution_duration = execution_end_time - execution_start_time
        click.echo("--" * 20)
        click.echo(f"Build completed for {self.name} v{self.version}")
        click.echo(f"Ran {len(summary)} automation steps in {execution_duration:.3f}s")
        headers = map(
            lambda h: f"{Fore.WHITE}{Style.BRIGHT}{h}{Style.RESET_ALL}",
            ["#", "STEP", "COMMAND", "STATUS"],
        )
        click.echo(
            tabulate(
                summary,
                headers=list(headers),
                showindex=False,
                tablefmt="github",
                numalign="center",
            )
        )

        if export_logs:
            log_file = self.__create_log_output(
                executed_steps, execution_duration, dry_run_mode
            )
            click.echo(f"\nStep execution summary saved to {log_file}")

        if failed_step:
            raise AeternumRuntimeError(
                f"Step '{failed_step.name}' failed with exit code {failed_step.exit_code}:"
                + f"\n{failed_step.stderr}"
            )
