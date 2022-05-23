# coding: utf-8
import unittest

from otrs_somconnexio.otrs_models.adsl_data import ADSLData


class ADSLDataTestCase(unittest.TestCase):

    def test_init(self):
        adsl_data = ADSLData(
            order_id=123,
            phone_number="666666666",
            iban="ES6621000418401234567891",
            email="test@test.com",
            previous_provider="SC",
            previous_internal_provider=None,
            previous_owner_vat="740227654G",
            previous_owner_name="name",
            previous_owner_surname="surname",
            service_address="address",
            service_city="city",
            service_zip="08001",
            service_subdivision="Barcelona",
            service_subdivision_code="ES-B",
            shipment_address="address",
            shipment_city="city",
            shipment_zip="08001",
            shipment_subdivision="ES-B",
            previous_service="ADSL",
            notes="Notes",
            adsl_coverage=None,
            mm_fiber_coverage=None,
            vdf_fiber_coverage=None,
            orange_fiber_coverage=None,
            type="location_change",
            landline_phone_number="landline_phone_number",
            product="product"
        )

        self.assertIsInstance(adsl_data, ADSLData)
