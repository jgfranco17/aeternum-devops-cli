import datetime as dt
import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import List, Optional

import click
import yaml
from colorama import Fore, Style
from pydantic import BaseModel, Field, ValidationError
from tabulate import tabulate

from aeternum.core.constants import StepExecutionStatus, StepType
from aeternum.core.errors import AeternumInputError, AeternumRuntimeError
from aeternum.core.output import get_command_string

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StepExecutionResult:
    name: str
    command_executed: str
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
        cmd_exec = get_command_string(self.command, self.args)
        full_cmd = [self.shell, "-c", cmd_exec]
        click.echo(f"Executing command: '{cmd_exec}'")
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        return StepExecutionResult(
            name=self.name,
            command_executed=cmd_exec,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
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

    def __create_log_output(
        self, steps: List[AutomationStep], duration: float, dry_run_mode: bool
    ):
        """Write execution log to file.

        Args:
            steps (List[AutomationStep]): Automation steps executed
            duration (float): Total dura
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
            log_summary_rows.append([idx, step.name, step.shell, command, status])
            step_counts_by_status[status] += 1

        log_summary_headers = ["#", "NAME", "SHELL", "COMMAND", "STATUS"]
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
            file.write(f"Execution duration: {duration:.3f}s\n\n")
            file.write("Step Summary:\n")
            for status, count in step_counts_by_status.items():
                file.write(f"{status}: {count}\n")
            file.write("\n")
            file.write(f"Build Output ({mode}):\n")
            file.write(step_summary_report)
            file.write("\n")

    def build(self, dry_run: bool, quiet: bool, save_output: bool) -> None:
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
        executed_steps = []
        summary = []
        failed_step = None
        execution_start_time = perf_counter()
        with build_progress as builds:
            for idx, step in enumerate(builds, start=1):
                click.echo(
                    f"\n[{idx} / {len(self.build_stage.steps)}][{step.type.upper()}]: {step.name}"
                )
                if not dry_run:
                    result = step.run()
                    if result.exit_code != 0:
                        icon = f"{Fore.RED}{Style.BRIGHT}{StepExecutionStatus.FAILED}{Style.RESET_ALL}"
                        summary.append([idx, step.name, icon])
                        executed_steps.append((step, StepExecutionStatus.FAILED))
                        failed_step = result
                        break
                    if not quiet:
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

        if save_output:
            log_file = self.__create_log_output(
                executed_steps, execution_duration, dry_run
            )
            click.echo(f"\nStep execution summary saved to {log_file}")

        if failed_step:
            raise AeternumRuntimeError(
                f"Step '{failed_step.name}' failed with exit code {failed_step.exit_code}:"
                + f"\n{failed_step.stderr}"
            )
