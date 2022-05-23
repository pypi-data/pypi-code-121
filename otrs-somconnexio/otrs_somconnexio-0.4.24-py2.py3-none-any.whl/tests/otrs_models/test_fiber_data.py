# coding: utf-8
import unittest

from otrs_somconnexio.otrs_models.fiber_data import FiberData


class FiberDataTestCase(unittest.TestCase):

    def test_init(self):
        fiber_data = FiberData(
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
            previous_service="Fiber",
            notes="Notes",
            adsl_coverage=None,
            mm_fiber_coverage=None,
            vdf_fiber_coverage=None,
            orange_fiber_coverage=None,
            type="new",
            product="product",
            previous_contract_address="Old street",
            previous_contract_phone="62626826",
            previous_contract_fiber_speed="100Mb",
            previous_contract_pon="VDF0001"
        )

        self.assertIsInstance(fiber_data, FiberData)
