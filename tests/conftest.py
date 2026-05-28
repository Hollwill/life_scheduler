import datetime

import pytest


@pytest.fixture
def now() -> datetime.datetime:
    return datetime.datetime.now()
