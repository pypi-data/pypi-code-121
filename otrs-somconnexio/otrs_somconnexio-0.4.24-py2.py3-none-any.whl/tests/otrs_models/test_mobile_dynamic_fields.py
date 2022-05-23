import unittest
from mock import Mock

from otrs_somconnexio.otrs_models.mobile_dynamic_fields import MobileDynamicFields


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


class MobileDynamicFieldsTestCase(unittest.TestCase):
    def setUp(self):
        self.customer_data = Mock(spec=[
            'id',
            'vat_number',
            'phone',
            'name',
            'first_name',
            'street',
            'zip',
            'city',
            'subdivision',
        ])
        self.mobile_data = Mock(spec=[
            'order_id',
            'phone_number',
            'iban',
            'email',
            'sc_icc',
            'icc',
            'service_internet_unlimited',
            'type',
            'previous_owner_vat',
            'previous_owner_name',
            'previous_owner_surname',
            'previous_provider',
            'product',
            'has_sim',
            'type',
            'delivery_street',
            'delivery_city',
            'delivery_zip_code',
            'delivery_state',
        ])
        self.mobile_data.type = 'new'

        self.mobile_otrs_process_id = "MobileProcessID"
        self.mobile_otrs_activity_id = "MobileActivityID"

    def test_process_id_field(self):
        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ProcessManagementProcessID"], "MobileProcessID")

    def test_activity_id_field(self):
        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ProcessManagementActivityID"], "MobileActivityID")

    def test_first_name_field(self):
        self.customer_data.first_name = 'First Name'

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["nomSoci"], "First Name")

    def test_name_field(self):
        self.customer_data.name = 'Name'

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["cognom1"], "Name")

    def test_vat_number_field(self):
        self.customer_data.vat_number = 'NIFCode'

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["NIFNIESoci"], "NIFCode")

    def test_line_field(self):
        self.mobile_data.phone_number = '666666666'

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["liniaMobil"], "666666666")

    def test_icc_sc_field(self):
        self.mobile_data.sc_icc = '1234'

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ICCSC"], "1234")

    def test_icc_donor_field(self):
        self.mobile_data.icc = '4321'

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["ICCdonant"], "4321")

    def test_service_type_field_new(self):
        self.mobile_data.type = 'new'

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["tipusServeiMobil"], "altaNova")

    def test_service_type_field_portability(self):
        self.mobile_data.type = 'portability'

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["tipusServeiMobil"], "portabilitat")

    def test_service_has_sim_field_true(self):
        self.mobile_data.has_sim = True

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertTrue(dynamic_fields_dct["noCobrarSIM"])

    def test_service_send_sim_type_has_sim_true(self):
        self.mobile_data.has_sim = True

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["tipusEnviamentSIM"], "None")

    def test_service_send_sim_type_has_sim_false(self):
        self.mobile_data.has_sim = False

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["tipusEnviamentSIM"], "CH_SC_OSO_SIM")

    def test_IBAN_field(self):
        self.mobile_data.iban = "ES6621000418401234567891"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["IBAN"], "ES6621000418401234567891")

    def test_contact_email_field(self):
        self.mobile_data.email = "test@email.org"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["correuElectronic"], "test@email.org")

    def test_contact_phone_field(self):
        self.customer_data.phone = "666666666"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["telefonContacte"], "666666666")

    def test_previous_provider_field(self):
        self.mobile_data.previous_provider = "AireNubip"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["operadorDonantMobil"], "AireNubip")

    # Portability
    def test_previous_owner_vat_portability(self):
        self.mobile_data.previous_owner_vat = "1234G"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["dniTitularAnterior"], "1234G")

    def test_previous_owner_name_portability(self):
        self.mobile_data.previous_owner_name = "Josep"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["titular"], "Josep")

    def test_previous_owner_first_name_portability(self):
        self.mobile_data.previous_owner_surname = "Nadal"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["cognom1Titular"], "Nadal")

    def test_product_field(self):
        self.mobile_data.product = "SE_SC_MOB_100_100"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["productMobil"], "SE_SC_MOB_100_100")

    def test_street_field(self):
        self.customer_data.street = "Les Moreres"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["nomVia"], "Les Moreres")

    def test_city_field(self):
        self.customer_data.city = "Alacant"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["localitat"], "Alacant")

    def test_zip_field(self):
        self.customer_data.zip = "03140"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["codiPostal"], "03140")

    def test_subdivision_field(self):
        self.customer_data.subdivision = "ES-A"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["provinciaMobil"], "ES-A")

    def test_delivery_street_field(self):
        self.mobile_data.delivery_street = "Les Moreres"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["direccioEnviament"], "Les Moreres")

    def test_delivery_city_field(self):
        self.mobile_data.delivery_city = "Alacant"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["poblacioEnviament"], "Alacant")

    def test_delivery_zip_code_field(self):
        self.mobile_data.delivery_zip_code = "03140"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["CPenviament"], "03140")

    def test_delivery_state_field(self):
        self.mobile_data.delivery_state = "ES-A"

        dynamic_fields = MobileDynamicFields(
            self.mobile_data,
            self.customer_data,
            self.mobile_otrs_process_id,
            self.mobile_otrs_activity_id
        ).all()

        dynamic_fields_dct = dynamic_fields_to_dct(dynamic_fields)
        self.assertEqual(dynamic_fields_dct["provinciaEnviament"], "ES-A")

