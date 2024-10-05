from tests.shared.runner import TestRunner


def test_help_message_sane(runner: TestRunner) -> None:
    """Test a sane basic help call."""
    result = runner.run_cli(["--help"])
    assert result.exit_code == 0
    assert (
        "Aeternum: CLI tool for managing containers and virtual machines"
        in result.output
    )
    assert "Author" in result.output, "Author info should be present"
    assert "Github" in result.output, "Github repo info should be present"


def test_invalid_command(runner: TestRunner) -> None:
    """Test a sane basic help call."""
    result = runner.run_cli(["invalid"])
    assert result.exit_code == 1
