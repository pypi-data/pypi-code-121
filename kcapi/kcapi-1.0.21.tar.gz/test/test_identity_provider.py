import unittest, time
from .testbed import TestBed
import json


def load_sample(fname):
    f = open(fname)
    file1 = json.loads(f.read())
    f.close()
    return file1


class TestingUserAPI(unittest.TestCase):

    def test_identity_provider_adding_saml_and_oid_IDP_providers(self):
        idp1 = self.kc.build('identity-provider', self.REALM)
        idp = self.kc.build('idp', self.REALM)
        saml = load_sample('./test/payloads/idp_saml.json')
        oid = load_sample('./test/payloads/idp_oid.json')
        state1 = idp.create(saml).isOk()
        self.assertTrue(state1)

        state2 = idp1.create(oid).isOk()
        self.assertTrue(state2)

        resources = idp1.all()

        self.assertEqual(resources[0]['alias'], saml['alias'], 'SAML alias should match')
        self.assertEqual(resources[1]['alias'], oid['alias'], 'SAML alias should match')

    @classmethod
    def setUpClass(self):
        self.testbed = TestBed()
        self.testbed.createRealms()
        self.testbed.createUsers()
        self.testbed.createClients()
        self.REALM = self.testbed.REALM
        self.kc = self.testbed.getKeycloak()

    @classmethod
    def tearDownClass(self):
        # self.testbed.goodBye()
        return True


if __name__ == '__main__':
    unittest.main()
