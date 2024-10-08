import logging
from typing import Generator, Tuple
from unittest.mock import MagicMock, patch

import pytest

from aeternum.core.output import ColorHandler
from tests.shared.runner import TestRunner


class MockLogger:
    def __init__(self) -> None:
        self.logger = logging.getLogger("mock-logger")
        self.logger.setLevel(logging.DEBUG)
        self.handler = ColorHandler()
        self.logger.addHandler(self.handler)

    def get_log_and_handler(self) -> Tuple[logging.Logger, ColorHandler]:
        return self.logger, self.handler


@pytest.fixture
def runner() -> TestRunner:
    return TestRunner()


@pytest.fixture
def logger() -> MockLogger:
    return MockLogger()


@pytest.fixture
def mock_datetime() -> Generator[MagicMock, None, None]:
    with patch("aeternum.core.models.dt.datetime") as mock_datetime:
        yield mock_datetime


@pytest.fixture
def mock_perf_counter() -> Generator[MagicMock, None, None]:
    with patch("aeternum.core.models.perf_counter") as mock_datetime:
        yield mock_datetime
