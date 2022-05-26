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
from sense.client.profile_api import ProfileApi
from sense.common import loadJSON
#


class TestProfileApi(unittest.TestCase):
    @classmethod
    def preOpCreate(cls):
        paths = [
            "requests/profile-1.json", "requests/profile-2.json"
        ]
        for path in paths:
            profile = loadJSON(path)
            res = cls.client.profile_create(json.dumps(profile))
            cls.uuids.append(res)

    @classmethod
    def setUpClass(cls):
        cls.uuids = []
        cls.client = ProfileApi()
        cls.preOpCreate()
        print(f"\nProfile Test :: using dummy instance: {cls.uuids[0]}")

    @classmethod
    def tearDownClass(cls):
        print(f'Profile Test :: cleaning up {len(cls.uuids)} dummy instances.')
        for uuid in cls.uuids:
            cls.client.profile_delete(uuid)

    def setUp(self) -> None:
        self.client = ProfileApi()

    def tearDown(self) -> None:
        pass

    def test_create_profile(self):
        # - TESTING: POST /
        profile = loadJSON("requests/profile-1.json")
        res = self.client.profile_create(json.dumps(profile))
        # print(f'ADD: {res}')
        assert re.match(
            '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            res)
        TestProfileApi.uuids.append(res)

    def test_get_profiles(self):
        # PRE-OP: load profile from class cache.
        uuid = TestProfileApi.uuids[0]
        #

        #
        # - TESTING: GET /
        res = json.loads(self.client.profile_list())
        for prof in res:
            if prof.get('uuid') == uuid:
                found = True
                break
        else:
            found = False
        assert found

        #
        # - TESTING: GET /{uuid}
        res = self.client.profile_describe(uuid)
        prof = json.loads(res)
        assert prof.get('uuid') == uuid

    def test_delete_profile(self):
        # PRE-OP: create profile for deletion test.
        self.test_create_profile()
        uuid = TestProfileApi.uuids.pop()
        #

        #
        # - TESTING: DELETE /{uuid}
        self.client.profile_delete(uuid)
        res = self.client.profile_describe(uuid)
        assert not res

    def test_update_profile(self):
        # PRE-OP: create profile for modification test.
        self.test_create_profile()
        uuid = TestProfileApi.uuids[-1]
        #

        #
        # - TESTING: PUT /{uuid}
        input = loadJSON("requests/profile-2.json")
        self.client.profile_update(json.dumps(input), uuid)
        prof = json.loads(self.client.profile_describe(uuid))
        assert prof.get('name') == input.get('name')

    def test_profile_uses(self):
        # PRE-OP: load profile from class cache.
        uuid = TestProfileApi.uuids[0]
        #
        #
        # - TESTING: GET /{uuid}/uses/{username}
        res = self.client.profile_get_uses(uuid, "admin")
        assert res == '0'

    def test_profile_license(self):
        # PRE-OP: create profile for deletion test.
        self.test_create_profile()
        uuid = TestProfileApi.uuids[-1]
        #

        #
        # - TESTING: POST /{uuid}/licenses
        license = loadJSON("requests/profile-license-1.json")
        self.client.profile_add_licenses(json.dumps(license), uuid)
        prof = json.loads(self.client.profile_describe(uuid))
        assert len(prof.get('licenses')) == 1

        #
        # - TESTING: PUT /{uuid}/licenses
        license.update({"remaining": 99})
        self.client.profile_update_licenses(json.dumps(license), uuid)
        prof = json.loads(self.client.profile_describe(uuid))
        assert prof.get('licenses')[0].get('remaining') == 99

        license.update({"remaining": 0})
        self.client.profile_update_licenses(json.dumps(license), uuid)
        prof = json.loads(self.client.profile_describe(uuid))
        assert len(prof.get('licenses')) == 0


if __name__ == '__main__':
    unittest.main()
