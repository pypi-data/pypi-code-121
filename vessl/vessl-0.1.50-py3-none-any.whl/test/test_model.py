import pytest

from test.conftest import USE_MOCK


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestModel:
    def test_create_model(self):
        # Do not test because requires completed experiment with no errors
        pass

    def test_list_models(self):
        # Test this after fully implemented model repository
        # vessl.list_models()
        pass

    def test_read_model(self):
        # Do not test because requires completed experiment with no errors
        pass

    def test_update_model(self):
        # Do not test because requires completed experiment with no errors
        pass

    def test_delete_model(self):
        # Do not test because requires completed experiment with no errors
        pass
