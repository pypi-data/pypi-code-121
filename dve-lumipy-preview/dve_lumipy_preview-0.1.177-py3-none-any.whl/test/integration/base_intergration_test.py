import unittest

import lumipy as lm
from test.unit.utilities.test_utils import load_secrets_into_env_if_local_run


class BaseIntegrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        load_secrets_into_env_if_local_run()
        cls.atlas = lm.get_atlas()
        cls.client = cls.atlas.get_client()
