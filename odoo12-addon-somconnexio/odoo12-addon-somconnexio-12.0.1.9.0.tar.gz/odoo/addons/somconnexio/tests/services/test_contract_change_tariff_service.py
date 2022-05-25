import odoo
import json
from datetime import date
from odoo.exceptions import UserError
from odoo.addons.easy_my_coop_api.tests.common import BaseEMCRestCase
from ...services.contract_change_tariff_process import ContractChangeTariffProcess
HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCaseAdmin(BaseEMCRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        # Skip parent class in super to avoid recreating api key
        super(BaseEMCRestCase, cls).setUpClass(*args, **kwargs)


class TestContractChangeTariffService(BaseEMCRestCaseAdmin):

    def setUp(self, *args, **kwargs):
        super().setUp()
        self.Contract = self.env['contract.contract']

        # Mobile
        self.phone = "654321123"
        self.old_mobile_product = self.browse_ref('somconnexio.TrucadesIllimitades1GB')
        self.new_mobile_product = self.browse_ref('somconnexio.TrucadesIllimitades2GB')
        self.mobile_data = {
            "product_code": self.new_mobile_product.default_code,
            "phone_number": self.phone,
        }
        contract_line = {
            "name": self.old_mobile_product.showed_name,
            "product_id": self.old_mobile_product.id,
            "date_start": "2020-01-01 00:00:00"
        }
        self.mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': self.phone,
            'icc': '123'
        })
        self.partner = self.browse_ref('base.partner_demo')
        self.mobile_contract = self.Contract.create({
            'name': 'Test Contract Mobile',
            'partner_id': self.partner.id,
            'service_partner_id': self.partner.id,
            'invoice_partner_id': self.partner.id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_mobile"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_masmovil"
            ),
            'mobile_contract_service_info_id': (
                self.mobile_contract_service_info.id
            ),
            'contract_line_ids': [
                (0, False, contract_line)
            ]
        })

        # Fiber contract
        self.code = '2222'
        self.old_fiber_product = self.browse_ref('somconnexio.Fibra600Mb')
        self.new_fiber_product = self.browse_ref('somconnexio.Fibra100Mb')
        self.fiber_data = {
            "product_code": self.new_fiber_product.default_code,
            "code": self.code,
        }

        self.mm_fiber_contract_service_info = self.env[
            'mm.fiber.service.contract.info'
        ].create({
            'phone_number': '972575757',
            'mm_id': '123'
        })
        fiber_contract_line = {
            "name": self.old_fiber_product.showed_name,
            "product_id": self.old_fiber_product.id,
            "date_start": "2020-01-01 00:00:00"
        }
        self.fiber_contract = self.Contract.create({
            'name': 'Test Contract Fiber',
            'code': self.code,
            'partner_id': self.partner.id,
            'service_partner_id': self.partner.id,
            'invoice_partner_id': self.partner.id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_fiber"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_masmovil"
            ),
            'mm_fiber_service_contract_info_id': (
                self.mm_fiber_contract_service_info.id
            ),
            'contract_line_ids': [
                (0, False, fiber_contract_line)
            ]
        })
        self.url = "/public-api/change-tariff"

    def http_public_post(self, url, data, headers=None):
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)
        return self.session.post(url, json=data)

    def test_route_right_run_wizard_mobile_without_date(self):
        response = self.http_public_post(self.url, data=self.mobile_data)

        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)
        partner_activities = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)],
        )
        created_activity = partner_activities[-1]

        self.assertTrue(self.mobile_contract.contract_line_ids[0].date_end)
        self.assertEqual(self.mobile_contract.contract_line_ids[0].product_id,
                         self.old_mobile_product)
        self.assertFalse(self.mobile_contract.contract_line_ids[1].date_end)
        self.assertEqual(self.mobile_contract.contract_line_ids[1].date_start,
                         ContractChangeTariffProcess.get_first_day_of_next_month(date.today()))  # noqa
        self.assertEqual(self.mobile_contract.contract_line_ids[1].product_id,
                         self.new_mobile_product)
        self.assertEquals(created_activity.summary, 'Canvi de tarifa a {}'.format(
            self.new_mobile_product.showed_name))

    def test_route_right_mobile_with_start_date(self):
        start_date = "2022-03-01"
        self.mobile_data.update({"start_date": start_date})
        expected_start_date = date(2022, 3, 1)
        expected_finished_date = date(2022, 2, 28)

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)

        self.assertEqual(self.mobile_contract.contract_line_ids[0].date_end,
                         expected_finished_date)
        self.assertEqual(self.mobile_contract.contract_line_ids[0].product_id,
                         self.old_mobile_product)
        self.assertFalse(self.mobile_contract.contract_line_ids[1].date_end)
        self.assertEqual(self.mobile_contract.contract_line_ids[1].date_start,
                         expected_start_date)
        self.assertEqual(self.mobile_contract.contract_line_ids[1].product_id,
                         self.new_mobile_product)

    def test_route_right_mobile_with_OTRS_formatted_date(self):
        start_date = "2022-03-01 00:00:00"
        self.mobile_data.update({"start_date": start_date})
        expected_start_date = date(2022, 3, 1)
        expected_finished_date = date(2022, 2, 28)

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)

        self.assertEqual(self.mobile_contract.contract_line_ids[0].date_end,
                         expected_finished_date)
        self.assertEqual(self.mobile_contract.contract_line_ids[0].product_id,
                         self.old_mobile_product)
        self.assertFalse(self.mobile_contract.contract_line_ids[1].date_end)
        self.assertEqual(self.mobile_contract.contract_line_ids[1].date_start,
                         expected_start_date)
        self.assertEqual(self.mobile_contract.contract_line_ids[1].product_id,
                         self.new_mobile_product)

    def test_route_right_mobile_empty_start_date(self):
        self.mobile_data.update({"start_date": ""})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.mobile_data)
        expected_start_date = process.get_first_day_of_next_month(date.today())

        self.assertTrue(self.mobile_contract.contract_line_ids[0].date_end)
        self.assertEqual(self.mobile_contract.contract_line_ids[0].product_id,
                         self.old_mobile_product)
        self.assertFalse(self.mobile_contract.contract_line_ids[1].date_end)
        self.assertEqual(self.mobile_contract.contract_line_ids[1].date_start,
                         expected_start_date)
        self.assertEqual(self.mobile_contract.contract_line_ids[1].product_id,
                         self.new_mobile_product)

    def test_route_bad_mobile_phone(self):
        wrong_phone = "8383838"
        self.mobile_data.update({"phone_number": wrong_phone})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaisesRegex(
            UserError,
            "Mobile contract not found with phone: {}".format(wrong_phone),
            process.run_from_api, **self.mobile_data
        )

    def test_route_bad_product(self):
        wrong_product = "FAKE_DEFAULT_CODE"
        self.mobile_data.update({"product_code": wrong_product})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaisesRegex(
            UserError,
            "Product not found with code: {}".format(
                wrong_product),
            process.run_from_api, **self.mobile_data
        )

    def test_route_bad_date(self):
        wrong_date = "202-202-202"
        self.mobile_data.update({"start_date": wrong_date})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaisesRegex(
            UserError,
            "Date with unknown format: {}".format(wrong_date),
            process.run_from_api, **self.mobile_data
        )

    def test_route_neither_phone_nor_code(self):
        self.mobile_data.update({"phone_number": "", "code": ""})

        response = self.http_public_post(self.url, data=self.mobile_data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaises(UserError, process.run_from_api, **self.mobile_data)

    def test_route_right_run_wizard_fiber_without_date(self):
        response = self.http_public_post(self.url, data=self.fiber_data)

        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.fiber_data)
        partner_activities = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)],
        )
        created_activity = partner_activities[-1]

        self.assertTrue(self.fiber_contract.contract_line_ids[0].date_end)
        self.assertEqual(self.fiber_contract.contract_line_ids[0].product_id,
                         self.old_fiber_product)
        self.assertFalse(self.fiber_contract.contract_line_ids[1].date_end)
        self.assertEqual(self.fiber_contract.contract_line_ids[1].date_start,
                         ContractChangeTariffProcess.get_first_day_of_next_month(date.today()))  # noqa
        self.assertEqual(self.fiber_contract.contract_line_ids[1].product_id,
                         self.new_fiber_product)
        self.assertEquals(created_activity.summary, 'Canvi de tarifa a {}'.format(
            self.new_fiber_product.showed_name))

    def test_route_right_fiber_with_start_date(self):
        start_date = "2022-03-01"
        self.fiber_data.update({"start_date": start_date})
        expected_start_date = date(2022, 3, 1)
        expected_finished_date = date(2022, 2, 28)

        response = self.http_public_post(self.url, data=self.fiber_data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)
        process.run_from_api(**self.fiber_data)

        self.assertEqual(self.fiber_contract.contract_line_ids[0].date_end,
                         expected_finished_date)
        self.assertEqual(self.fiber_contract.contract_line_ids[0].product_id,
                         self.old_fiber_product)
        self.assertFalse(self.fiber_contract.contract_line_ids[1].date_end)
        self.assertEqual(self.fiber_contract.contract_line_ids[1].date_start,
                         expected_start_date)
        self.assertEqual(self.fiber_contract.contract_line_ids[1].product_id,
                         self.new_fiber_product)

    def test_route_bad_fiber_contract_code(self):
        wrong_code = "inexisting_code"
        self.fiber_data.update({"code": wrong_code})

        response = self.http_public_post(self.url, data=self.fiber_data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = ContractChangeTariffProcess(self.env)

        self.assertRaisesRegex(
            UserError,
            "Contract not found with code: {}".format(wrong_code),
            process.run_from_api, **self.fiber_data
        )
