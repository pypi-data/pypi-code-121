from unittest.mock import Mock

import pytest


@pytest.fixture()
def logger():
    return Mock()
