import unittest
from mock import Mock

from otrs_somconnexio.otrs_models.router_4G_dynamic_fields import Router4GDynamicFields


def dynamic_fields_to_dct(dynamic_fields):
    """
    Convert the Router4GDynamicFields object in a dict with the name of the dynamic
    field as key and the value as value.
    Only used to test the Router4GDynamicFields object.
    """
    dct = {}
    for df in dynamic_fields:
        dct[df.name] = df.value
    return dct


class Router4GDynamicFieldsTestCase(unittest.TestCase):
    def setUp(self):
        self.customer_data = Mock(spec=[
            'first_name',
            'name',
            'vat_number',
            'phone',
        ])
        self.service_data = Mock(spec=[
            'order_id',
            'previous_contract_address',
            'previous_contract_phone',
            'iban',
            'email',
            'phone_number',
            'service_address',
            'service_city',
            'service_zip',
            'service_subdivision',
            'service_subdivision_code',
            'shipment_address',
            'shipment_city',
            'shipment_zip',
            'shipment_subdivision',
            'previous_service',
            'previous_provider',
            'previous_owner_vat',
            'previous_owner_name',
            'previous_owner_surname',
            'notes',
            'adsl_coverage',
            'mm_fiber_coverage',
            'vdf_fiber_coverage',
            'orange_fiber_coverage',
            'type',
            'product',
            'previous_internal_provider',
        ])

        self.router_4G_otrs_process_id = "Router4GProcessID"
        self.router_4G_otrs_activity_id = "Router4GActivityID"

    def test_process_id_field(self):
        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ProcessManagementProcessID"], "Router4GProcessID")


    def test_activity_id_field(self):
        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ProcessManagementActivityID"], "Router4GActivityID")

    def test_previous_phone_field(self):
        self.service_data.previous_contract_phone = "666666666"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(
            dynamic_fields_dct["telefonFixAntic"],
            self.service_data.previous_contract_phone
        )

    def test_previous_address_field(self):
        self.service_data.previous_contract_address = "Old street"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(
            dynamic_fields_dct["direccioServeiAntic"],
            self.service_data.previous_contract_address
        )

    # TODO: Are we using this field?????
    def test_contract_id_field(self):
        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["IDContracte"], self.service_data.order_id)

    def test_first_name_field(self):
        self.customer_data.first_name = "First Name"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["nomSoci"], "First Name")

    def test_name_field(self):
        self.customer_data.name = "Surname"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["cognom1"], "Surname")

    def test_vat_number_field(self):
        self.customer_data.vat_number = "NIFCode"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["NIFNIESoci"], "NIFCode")

    def test_IBAN_field(self):
        self.service_data.iban = "ES6621000418401234567891"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["IBAN"], "ES6621000418401234567891")

    def test_contact_phone_field(self):
        self.customer_data.phone = "666666666"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["telefonContacte"], "666666666")

    def test_contact_email_field(self):
        self.service_data.email = "test@email.org"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["correuElectronic"], "test@email.org")

    def test_previous_service_field(self):
        self.service_data.previous_service = "ADSL"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["serveiPrevi"], "ADSL")

    def test_previous_provider_field(self):
        self.service_data.previous_provider = "SomConnexio"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["proveidorPrevi"], "SomConnexio")

    def test_landline_number_field(self):
        self.service_data.phone_number = "666666666"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["telefonFixVell"], "666666666")

    def test_address_field(self):
        self.service_data.service_address = "Street"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["direccioServei"], "Street")

    def test_city_field(self):
        self.service_data.service_city = "City"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["poblacioServei"], "City")

    def test_zip_field(self):
        self.service_data.service_zip = "000000"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["CPservei"], "000000")

    def test_subdivision_field(self):
        self.service_data.service_subdivision = "Subdivision"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["provinciaServei"], "Subdivision")

    def test_subdivision_code_field(self):
        self.service_data.service_subdivision_code = "ES-B"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["codiProvinciaServei"], "ES-B")

    def test_shipment_address_field(self):
        self.service_data.shipment_address = "Street"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["direccioEnviament"], "Street")

    def test_shipment_city_field(self):
        self.service_data.shipment_city = "City"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["poblacioEnviament"], "City")

    def test_shipment_zip_field(self):
        self.service_data.shipment_zip = "000000"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["CPenviament"], "000000")

    def test_shipment_subdivision_field(self):
        self.service_data.shipment_subdivision = "Subdivision"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["provinciaEnviament"], "Subdivision")

    def test_owner_vat_field(self):
        self.service_data.previous_owner_vat = "12345M"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["NIFNIEtitular"], "12345M")

    def test_owner_name_field(self):
        self.service_data.previous_owner_name = "Name"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["titular"], "Name")

    def test_owner_surname_field(self):
        self.service_data.previous_owner_surname = "Surname"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["cognom1Titular"], "Surname")

    def test_adsl_coverage_field(self):
        self.service_data.adsl_coverage = "20"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["coberturaADSL"], "20")

    def test_mm_fiber_coverage_field(self):
        self.service_data.mm_fiber_coverage = "fibraFTTH"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["coberturaFibraMM"], "fibraFTTH")

    def test_vdf_fiber_coverage_field(self):
        self.service_data.vdf_fiber_coverage = "fibraFTTH"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["coberturaFibraVdf"], "fibraFTTH")

    def test_orange_fiber_coverage_field(self):
        self.service_data.orange_fiber_coverage = "fibraFTTH"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["coberturaFibraOrange"], "fibraFTTH")

    def test_type_field_location_change(self):
        self.service_data.type = "location_change"
        self.service_data.previous_owner_name = "A"
        self.service_data.previous_owner_surname = "B"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["canviUbicacioMateixTitular"], "yes")
        self.assertEqual(dynamic_fields_dct["nomCognomSociAntic"], "A B")

    def test_type_field_non_location_change(self):
        self.service_data.type = "portability"
        self.service_data.previous_owner_name = "A"
        self.service_data.previous_owner_surname = "B"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["canviUbicacioMateixTitular"], "no")
        self.assertNotIn("nomCognomSociAntic", dynamic_fields_dct.keys())

    def test_product_field(self):
        self.service_data.product = "Router4Gproduct"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["productBA"], "Router4Gproduct")

    def test_previous_provider_CU_field(self):
        self.service_data.previous_internal_provider = "SC-MM"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["proveidorPreviCU"], "SC-MM")

    def test_previous_provider_does_not_exist_when_location_change(self):
        self.service_data.type = "location_change"

        dynamic_fields = Router4GDynamicFields(
            self.service_data,
            self.customer_data,
            self.router_4G_otrs_process_id,
            self.router_4G_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertNotIn("proveidorPrevi", dynamic_fields_dct.keys())
