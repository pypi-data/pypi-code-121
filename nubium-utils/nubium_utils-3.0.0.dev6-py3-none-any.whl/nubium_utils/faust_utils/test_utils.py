# Allows for testing Faust functions via pytest (handles async) while stylizing your tests as unittests

from unittest.mock import Mock


class AsyncMock(Mock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


class AsyncTestCase(object):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def setup_method(self):
        self.setUp()

    def teardown_method(self):
        self.tearDown()

    def __getattribute__(self, item):
        method = object.__getattribute__(self, item)
        if method is None:
            raise AttributeError(f"Unknown object as no attribute '{item}'")
        return method
