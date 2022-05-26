import unittest, time
from .testbed import TestBed
import json


def load_sample(file_name):
    f = open(file_name)
    payload = json.loads(f.read())
    f.close()

    return payload


class TestingRealmAPI(unittest.TestCase):

    def testing_realm_api_methods(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)
        self.assertTrue(hasattr(realms, 'caches'))


    def testing_realm_cache_reset(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)

        caches = realms.caches(self.REALM)

        self.assertEqual(caches.clearRealmCache().resp().status_code, 204)

    def testing_user_cache_reset(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)

        caches = realms.caches(self.REALM)
        self.assertEqual(caches.clearUserCache().resp().status_code, 204)

    def testing_key_cache_reset(self):
        realms = self.testbed.getKeycloak().build('realms', self.REALM)

        caches = realms.caches(self.REALM)

        self.assertEqual(caches.clearKeyCache().resp().status_code, 204)

    def testing_complex_realm_publishing(self):
        admin = self.testbed.getAdminRealm()
        realm_cfg = load_sample('./test/payloads/complex_realms.json')
        creation_state = admin.create(realm_cfg).isOk()
        self.assertTrue(creation_state, 'This realm should be created')



    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()


        self.REALM = self.testbed.REALM

    @classmethod
    def tearDownClass(self):
        self.testbed.goodBye()
        admin = self.testbed.getAdminRealm()
        realm_cfg = load_sample('./test/payloads/complex_realms.json')
        admin.removeFirstByKV("realm", realm_cfg["realm"], custom_key="realm")


if __name__ == '__main__':
    unittest.main()
