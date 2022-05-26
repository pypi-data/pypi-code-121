import os
import unittest
import pytest
import re
import json
import time
import sys

# Append root for proper imports
sys.path.append('')
#

#
from sense.client.discover_api import DiscoverApi
from sense.common import loadJSON
#


class TestDiscoverApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        res = json.loads(DiscoverApi().discover_get())
        cls.uri = res["domains"][0]["domain_uri"]
        print(f"\nDiscover Test :: using domain URI: {cls.uri}")

    def setUp(self) -> None:
        self.client = DiscoverApi()

    def tearDown(self) -> None:
        pass

    def test_get_full(self):
        # - TESTING: GET /discover
        res = json.loads(self.client.discover_get())
        assert "domains" in res

    def test_get_domains(self):
        # - TESTING: GET /discover/domains
        res = json.loads(self.client.discover_domains_get())
        assert "domains" in res

    def test_get_by_id(self):
        # - TESTING: GET /discover/{domainID}
        res = json.loads(
            self.client.discover_domain_id_get(TestDiscoverApi.uri))
        assert res["domain_uri"] == TestDiscoverApi.uri

    def test_get_by_id_peers(self):
        # - TESTING: GET /discover/{domainID}/peers
        res = json.loads(
            self.client.discover_domain_id_peers_get(TestDiscoverApi.uri))
        assert res["domain_uri"] == TestDiscoverApi.uri
        assert "peer_points" in res

    def test_get_instances(self):
        # - TESTING: GET /discover/service/instance
        res = json.loads(self.client.discover_service_instances_get())
        assert "instances" in res
        # TODO: leverage instance test suite to create dummy for query testing.

    @unittest.expectedFailure
    def test_lookup(self):
        # TODO: find better/consistent way to get correct query name. Expected to fail otherwise.
        # - TESTING: GET /discover/lookup/{name}
        res = json.loads(
            self.client.discover_lookup_name_get(TestDiscoverApi.uri))
        assert "results" in res
