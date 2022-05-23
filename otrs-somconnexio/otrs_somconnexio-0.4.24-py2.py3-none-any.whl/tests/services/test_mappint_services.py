import unittest

from otrs_somconnexio.services.mapping_services import ServiceMappingServices


class ServiceMappingServicesTestCase(unittest.TestCase):
    'Test service mapping services'

    def test_mapping_Fibra(self):
        'Test the mapping of service Fibra'
        self.assertEqual("fiber", ServiceMappingServices.service('Fibra'))

    def test_mapping_ADSL(self):
        'Test the mapping of service ADSL'
        self.assertEqual("adsl", ServiceMappingServices.service('ADSL'))

    def test_mapping_ADSL100(self):
        'Test the mapping of service ADSL + 100 min'
        self.assertEqual("adsl100", ServiceMappingServices.service('ADSL+100min'))

    def test_mapping_ADSL1000(self):
        'Test the mapping of service ADSL + 1000 min'
        self.assertEqual("adsl1000", ServiceMappingServices.service('ADSL+1000min'))
