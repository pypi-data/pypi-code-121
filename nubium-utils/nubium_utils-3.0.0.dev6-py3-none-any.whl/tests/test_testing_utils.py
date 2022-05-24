import unittest

from nubium_utils.faust_utils.test_utils import AsyncMock
from asyncio.coroutines import iscoroutine


class TestTestingUtils(unittest.TestCase):
    """
    Unit tests for testing utilities
    """

    def test_async_mock_str(self):
        """
        Calling str on the mock object should return a string

        Makes sure that certain dunder methods don't return a co-routine
        """
        mock = AsyncMock()
        assert str(mock) == f'<AsyncMock id=\'{id(mock)}\'>'

    def test_async_mock_method_call(self):
        """
        Undefined method calls should return a co-routine
        """
        mock = AsyncMock()
        assert iscoroutine(mock.foo())
