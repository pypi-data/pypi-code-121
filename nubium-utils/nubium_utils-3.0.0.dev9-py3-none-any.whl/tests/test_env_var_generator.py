import pytest
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch
from nubium_utils.env_var_generator import EnvVars


class TestEnvVarGenerator(TestCase):

    def setUp(self):
        self.dict_out = {"test_env_field": "test_env_value"}
        self.env_vars = EnvVars(self.dict_func)

    def dict_func(self):
        return self.dict_out

    def test_it_works(self):
        self.assertDictEqual(self.env_vars(), self.dict_out)

    def test_returns_same_python_object_each_call(self):
        self.assertEqual(id(self.env_vars()), id(self.env_vars()))  # also ensures subsequent calls work!

    def test__env_reload(self):
        self.env_vars()
        self.dict_out.update({'I_SHOULD_BE_ADDED_AFTER_RELOAD': 'plz'})
        assert 'I_SHOULD_BE_ADDED_AFTER_RELOAD' not in self.env_vars()
        self.env_vars._reload()
        assert 'I_SHOULD_BE_ADDED_AFTER_RELOAD' in self.env_vars()

if __name__ == '__main__':
    pytest.main([__file__])