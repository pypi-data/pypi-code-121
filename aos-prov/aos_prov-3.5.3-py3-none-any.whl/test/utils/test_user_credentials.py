import unittest

from aos_prov.utils.user_credentials import UserCredentials


class TestUserCredentials(unittest.TestCase):
    def test_attributes(self):
        uc = UserCredentials('zzz', 'zz1')

        uc.cert_type = 'type1'
        self.assertEqual(uc.cert_type, 'type1')

        uc.certificate = 'some cert 1'
        self.assertEqual(uc.certificate, 'some cert 1')

        uc.csr = 'csr'
        self.assertEqual(uc.csr, 'csr')
