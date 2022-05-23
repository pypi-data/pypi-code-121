import unittest

from otrs_somconnexio.otrs_models.telecom_company import TelecomCompany


class FakeTelecom:
    def __init__(self, name):
        self.name = name


class TelecomCompanyTestCase(unittest.TestCase):
    def test_mobile_telecom_company_none(self):
        tryton_telecom = None

        telecom = TelecomCompany('mobile', tryton_telecom)

        self.assertEqual(str(telecom), 'None')

    def test_mobile_telecom_company_other(self):
        tryton_telecom = FakeTelecom('New Som Connexio')

        telecom = TelecomCompany('mobile', tryton_telecom)

        self.assertEqual(str(telecom), 'Other')

    def test_mobile_telecom_company(self):
        tryton_telecom = FakeTelecom('Aire / Nubip')

        telecom = TelecomCompany('mobile', tryton_telecom)

        self.assertEqual(str(telecom), 'AireNubip')

    def test_internet_telecom_company_none(self):
        tryton_telecom = None

        telecom = TelecomCompany('internet', tryton_telecom)

        self.assertEqual(str(telecom), 'None')

    def test_internet_telecom_company_other(self):
        tryton_telecom = FakeTelecom('New Som Connexio')

        telecom = TelecomCompany('internet', tryton_telecom)

        self.assertEqual(str(telecom), 'Other')

    def test_broadband_telecom_company(self):
        tryton_telecom = FakeTelecom('Aire / Nubip')

        telecom = TelecomCompany('internet', tryton_telecom)

        self.assertEqual(str(telecom), 'Nubip')
