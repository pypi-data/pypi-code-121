import unittest

from aos_prov.utils.unit_certificate import UnitCertificate


class TestUnitCertificate(unittest.TestCase):
    def test_object_can_be_created(self):
        uc = UnitCertificate()
        self.assertIsInstance(uc, UnitCertificate)

    def test_attributes(self):
        uc = UnitCertificate()

        uc.cert_type = 'type1'
        self.assertEqual(uc.cert_type, 'type1')

        uc.certificate = 'some cert 1'
        self.assertEqual(uc.certificate, 'some cert 1')

        uc.csr = 'csr'
        self.assertEqual(uc.csr, 'csr')
