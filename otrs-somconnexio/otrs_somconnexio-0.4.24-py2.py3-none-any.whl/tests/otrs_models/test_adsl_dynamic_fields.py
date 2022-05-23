import unittest
from mock import Mock

from otrs_somconnexio.otrs_models.adsl_dynamic_fields import ADSLDynamicFields


def dynamic_fields_to_dct(dynamic_fields):
    """
    Convert the MobileDynamicFields object in a dict with the name of the dynamic
    field as key and the value as value.
    Only used to test the MobileDynamicFields object.
    """
    dct = {}
    for df in dynamic_fields:
        dct[df.name] = df.value
    return dct


class ADSLDynamicFieldsTestCase(unittest.TestCase):
    def setUp(self):
        self.customer_data = Mock(spec=[
            'first_name',
            'name',
            'vat_number',
            'phone',
        ])
        self.service_data = Mock(spec=[
            'order_id',
            'iban',
            'email',
            'phone_number',
            'landline_phone_number',
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
            'previous_contract_address',
            'previous_contract_phone',
            'notes',
            'adsl_coverage',
            'mm_fiber_coverage',
            'vdf_fiber_coverage',
            'orange_fiber_coverage',
            'type',
            'product',
            'previous_internal_provider',
        ])

        self.adsl_otrs_process_id = "ADSLProcessID"
        self.adsl_otrs_activity_id = "ADSLActivityID"

    def test_process_id_field(self):
        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ProcessManagementProcessID"], "ADSLProcessID")

    def test_activity_id_field(self):
        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ProcessManagementActivityID"], "ADSLActivityID")

    def test_contract_id_field(self):
        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["IDContracte"], self.service_data.order_id)

    def test_first_name_field(self):
        self.customer_data.first_name = "First Name"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["nomSoci"], "First Name")

    def test_name_field_organization_type(self):
        self.customer_data.name = "Surname"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["cognom1"], "Surname")

    def test_vat_number_field(self):
        self.customer_data.vat_number = "NIFCode"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["NIFNIESoci"], "NIFCode")

    def test_IBAN_field(self):
        self.service_data.iban = "ES6621000418401234567891"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["IBAN"], "ES6621000418401234567891")

    def test_contact_phone_field(self):
        self.customer_data.phone = "666666666"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["telefonContacte"], "666666666")

    def test_contact_email_field(self):
        self.service_data.email = "test@email.org"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["correuElectronic"], "test@email.org")

    def test_previous_service_field(self):
        self.service_data.previous_service = "ADSL"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["serveiPrevi"], "ADSL")

    def test_previous_provider_field(self):
        self.service_data.previous_provider = "Nubip"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["proveidorPrevi"], "Nubip")

    # TODO: Are we using this field??
    def test_old_landline_number_field(self):
        self.service_data.phone_number = "666666666"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["telefonFixVell"], "666666666")

    def test_service_address_field(self):
        self.service_data.service_address = "Street"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["direccioServei"], "Street")

    def test_service_city_field(self):
        self.service_data.service_city = "City"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["poblacioServei"], "City")

    def test_service_zip_field(self):
        self.service_data.service_zip = "000000"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["CPservei"], "000000")

    def test_service_subdivision_field(self):
        self.service_data.service_subdivision = "Subdivision"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["provinciaServei"], "Subdivision")

    def test_service_subdivision_code_field(self):
        self.service_data.service_subdivision_code = "ES-B"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["codiProvinciaServei"], "ES-B")

    def test_shipment_address_field(self):
        self.service_data.shipment_address = "Street"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["direccioEnviament"], "Street")

    def test_shipment_city_field(self):
        self.service_data.shipment_city = "City"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["poblacioEnviament"], "City")

    def test_shipment_zip_field(self):
        self.service_data.shipment_zip = "000000"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["CPenviament"], "000000")

    def test_shipment_subdivision_field(self):
        self.service_data.shipment_subdivision = "Subdivision"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["provinciaEnviament"], "Subdivision")

    def test_owner_vat_field(self):
        self.service_data.previous_owner_vat = "12345M"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["NIFNIEtitular"], "12345M")

    def test_owner_name_field(self):
        self.service_data.previous_owner_name = "Name"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["titular"], "Name")

    def test_owner_surname_field(self):
        self.service_data.previous_owner_surname = "Surname"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["cognom1Titular"], "Surname")

    def test_adsl_coverage_field(self):
        self.service_data.adsl_coverage = "20"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["coberturaADSL"], "20")

    def test_mm_fiber_coverage_field(self):
        self.service_data.mm_fiber_coverage = "fibraFTTH"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["coberturaFibraMM"], "fibraFTTH")

    def test_vdf_fiber_coverage_field(self):
        self.service_data.vdf_fiber_coverage = "fibraFTTH"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["coberturaFibraVdf"], "fibraFTTH")

    def test_orange_fiber_coverage_field(self):
        self.service_data.orange_fiber_coverage = "fibraFTTH"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["coberturaFibraOrange"], "fibraFTTH")

    # Service Dynamic Fields
    def test_landline_number_field(self):
        self.service_data.landline_phone_number = "666666666"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["mantenirFix"], "666666666")

    def test_product_field(self):
        self.service_data.product = "ADSL20+100"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["productBA"], "ADSL20+100")

    def test_previous_provider_CU_field(self):
        self.service_data.previous_internal_provider = "SC-MM"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["proveidorPreviCU"], "SC-MM")

    def test_type_field_location_change(self):
        self.service_data.type = "location_change"
        self.service_data.previous_owner_name = "A"
        self.service_data.previous_owner_surname = "B"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["canviUbicacioMateixTitular"], "yes")
        self.assertEqual(dynamic_fields_dct["nomCognomSociAntic"], "A B")

    def test_type_field_non_location_change(self):
        self.service_data.type = "portability"
        self.service_data.previous_owner_name = "A"
        self.service_data.previous_owner_surname = "B"

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["canviUbicacioMateixTitular"], "no")
        self.assertNotIn("nomCognomSociAntic", dynamic_fields_dct.keys())

    def test_previous_provider_does_not_exist_when_location_change(self):
        self.service_data.type = 'location_change'

        dynamic_fields = ADSLDynamicFields(
            self.service_data,
            self.customer_data,
            self.adsl_otrs_process_id,
            self.adsl_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertNotIn("proveidorPrevi", dynamic_fields_dct.keys())
