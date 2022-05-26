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
from sense.client.logging_api import LoggingApi
from sense.common import loadJSON
#


class TestLoggingApi(unittest.TestCase):
    def setUp(self) -> None:
        self.client = LoggingApi()

    def tearDown(self) -> None:
        pass

    def test_get_config(self):
        #
        # TESTING: GET /logging/config
        conf = json.loads(self.client.logging_get_config())
        assert conf.get("loggers").get("console")

    def test_set_filter(self):
        # PRE-OP: get current filter
        testString = ''.join(
            random.choice(string.ascii_lowercase) for i in range(10))
        pre_conf = json.loads(self.client.logging_get_config())
        if "filter" in pre_conf:
            pre = re.findall("pattern=(.*)", pre_conf.get("filter"))
        else:
            pre = None

        #
        # TESTING: PUT /logging/filter
        self.client.logging_set_filter(body=testString)
        conf = json.loads(self.client.logging_get_config())
        assert testString in conf.get("filter")

        # POST-OP: set old filter
        if pre and len(pre) > 0:
            self.client.logging_set_filter(body=pre[0])
        else:
            self.client.logging_set_filter()

    def test_put_level(self):
        # PRE-OP: get current console level
        pre_conf = json.loads(self.client.logging_get_config())
        pre_level = pre_conf.get("loggers").get("console")

        #
        # TESTING: PUT /logging/config/{logger}/{level}
        self.client.logging_set_logger_level("console", "ERROR")
        conf = json.loads(self.client.logging_get_config())
        assert conf.get("loggers").get("console") == "ERROR"

        # POST-OP: set old level
        if pre_level:
            self.client.logging_set_logger_level("console", pre_level)
        else:
            self.client.logging_set_logger_level("console", "INFO")

    def test_get_logs(self):
        #
        # TESTING: GET /logging/logs/{siUUID}
        # -- 1: full logs
        self.client.si_uuid = "null"
        res = json.loads(self.client.instance_get_logging())
        assert "data" in res and len(res.get("data")) > 0
        # -- 2: instance logs (if instances present)
        filtered = list(
            filter(lambda log: log.get("referenceUUID"), res.get("data")))
        if len(filtered) > 0:
            self.client.si_uuid = filtered[0].get("referenceUUID")
            filtered_res = json.loads(self.client.instance_get_logging())
            assert_filtered = list(
                filter(
                    lambda log: log.get("referenceUUID") != self.client.
                    si_uuid, filtered_res.get("data")))
            assert len(assert_filtered) == 0

    # TODO: implement safe archival test.
    def TODO_archive_logs(self):
        # TESTING: PUT /logging/archive/{days}
        pass


if __name__ == '__main__':
    unittest.main()
