from typing import Any, Tuple
from unittest.mock import MagicMock

from pytest_mock import MockerFixture


def get_mocked_function_and_output(
    mocker: MockerFixture, import_path: str
) -> Tuple[MagicMock, Any]:
    """Return a mocked fn and the the return value mock for a given path."""
    # The mock patch function
    mock_fn = mocker.patch(f"aeternum.{import_path}")
    # The return value that can be asserted on
    return_value = mock_fn.return_value
    return (mock_fn, return_value)
