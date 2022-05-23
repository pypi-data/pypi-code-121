import unittest

from otrs_somconnexio.services.mapping_mobile_minutes import ServiceMappingMobileMinutes


class ServiceMappingMobileMinutesTestCase(unittest.TestCase):
    def test_mapping_0(self):
        'Test the mapping of service Fibra'
        self.assertEqual("0", ServiceMappingMobileMinutes.minutes('0min'))

    def test_mapping_100(self):
        'Test the mapping of service Fibra'
        self.assertEqual("100", ServiceMappingMobileMinutes.minutes('100min'))

    def test_mapping_200(self):
        'Test the mapping of service Fibra'
        self.assertEqual("200", ServiceMappingMobileMinutes.minutes('200min'))

    def test_mapping_unlim(self):
        'Test the mapping of service Fibra'
        self.assertEqual("unlimited", ServiceMappingMobileMinutes.minutes('unlim'))
