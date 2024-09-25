import os

from pydantic import ValidationError
from pytest import raises

from aeternum.core.errors import AeternumInputError
from aeternum.core.models import (
    AutomationStep,
    AutomationStrategy,
    BuildStage,
    ProjectSpec,
)
from tests.test_helpers.file_utils import load_resources_dir


def test_load_from_yaml_success():
    spec_file = load_resources_dir("valid", "aeternum.yaml")
    project = ProjectSpec.load_from_yaml(spec_file)

    assert project.name == "test-project"
    assert project.repo_url == "https://github.com/some-user/my-test-project"
    assert project.version == "0.1.0"
    assert project.strict_build is True
    for step in project.build_stage.steps:
        assert isinstance(step, AutomationStep)
        assert step.type in ["build", "test", "deploy"]
        assert step.shell is not None


def test_load_from_yaml_defaults_success():
    spec_file = load_resources_dir("minimal", "aeternum.yaml")
    project = ProjectSpec.load_from_yaml(spec_file)
    for step in project.build_stage.steps:
        # Default to bash shell
        assert step.shell is not "/bin/bash"


def test_load_from_yaml_non_existent_file():
    spec_file = load_resources_dir("non-existent.yaml")
    with raises(AeternumInputError):
        _ = ProjectSpec.load_from_yaml(spec_file)


def test_load_from_yaml_invalid_file():
    spec_file = load_resources_dir("invalid_files", "invalid-file-type.json")
    with raises(AeternumInputError):
        _ = ProjectSpec.load_from_yaml(spec_file)


def test_build_stage_components_success():
    strategy = AutomationStrategy(strict=True)
    exec_steps = [
        AutomationStep(name="Run make", type="build", command="make", args=["build"]),
        AutomationStep(name="Unit test", type="test", command="pytest", args=["-v"]),
        AutomationStep(
            name="Push",
            type="deploy",
            command="kubectl",
            args=["apply", "-f", "manifests/resources.yaml"],
        ),
    ]
    mock_build = BuildStage(strategy=strategy, steps=exec_steps)
    step_validation = mock_build.validate()
    assert step_validation.build_step_count == 1
    assert step_validation.test_step_count == 1
    assert step_validation.deploy_step_count == 1
    assert step_validation.invalid_step_count == 0
    assert step_validation.is_valid()


def test_automation_step_invalid():
    with raises(ValidationError):
        _ = AutomationStep(
            name="Something", type="random", command="python3", args=["app.py"]
        )
