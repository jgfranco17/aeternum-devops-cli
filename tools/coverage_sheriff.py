from typing import Final

import coverage

MINIMUM_CODE_COVERAGE: Final[int] = 80
RED_BOLD: Final[str] = "\033[91;1m"
GREEN_BOLD: Final[str] = "\033[92;1m"
YELLOW_BOLD: Final[str] = "\033[93;1m"
END: Final[str] = "\033[0m"


def print_colored_message(message: str, color: str, **kwargs) -> None:
    print(f"{color}{message}{END}", **kwargs)


def get_code_coverage():
    cov = coverage.Coverage(branch=True)
    cov.load()
    return cov.report(file=None)


def validate_coverage_level(total_coverage: float, minimum: int) -> None:
    assert minimum < 100, "Minimum code coverage should be between 0 and 100."

    if total_coverage < minimum:
        print_colored_message(
            f"Code coverage is below {minimum}%, consider adding more tests.",
            color=RED_BOLD,
        )
        exit(1)
    elif minimum <= total_coverage < 100:
        print_colored_message(
            "Code coverage is at an acceptable level.", color=YELLOW_BOLD
        )
    else:
        print_colored_message(f"Good job! Code coverage at 100%.", color=GREEN_BOLD)


if __name__ == "__main__":
    total_cov = get_code_coverage()
    print("=" * 40)
    print(f"Code coverage is {total_cov:.2f}%")
    validate_coverage_level(total_cov, minimum=MINIMUM_CODE_COVERAGE)
