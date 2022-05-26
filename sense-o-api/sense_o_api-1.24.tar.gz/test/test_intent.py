import os
import unittest
import pytest
import re
import json
import string
import random
import sys

# Append root for proper imports
sys.path.append('')
#

#
from sense.client.intent_api import IntentApi
from sense.client.instance_api import InstanceApi
from sense.common import loadJSON
#


class TestIntentApi(unittest.TestCase):
    def setUp(self) -> None:
        self.client = IntentApi()

        self.instance_client = InstanceApi()
        self.instance_client.instance_new()
        input = loadJSON("requests/request-1.json")
        self.instance_client.instance_create(json.dumps(input))

        self.client.si_uuid = self.instance_client.si_uuid

    def tearDown(self) -> None:
        if self.instance_client.si_uuid is not None:
            self.instance_client.instance_delete()

    def test_get_intents(self):
        #
        # TESTING: - /intent/instance/{siUUID}
        res = json.loads(self.client.instance_get_intents())
        assert len(res) > 0 and res[0].get("id")

    def test_get_intent_id(self):
        # PRE-OP: get uuid from test instance.
        uuid = json.loads(self.client.instance_get_intents())[0].get("id")

        #
        # TESTING: - /intent/{uuid}
        res = json.loads(self.client.intent_describe(uuid))
        assert res.get("id") == uuid


if __name__ == '__main__':
    unittest.main()
