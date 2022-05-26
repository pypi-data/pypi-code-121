import json
import odoo

from ..common_service import BaseEMCRestCaseAdmin
from ..helpers import subscription_request_create_data


class TestResPartnerController(BaseEMCRestCaseAdmin):

    def setUp(self):
        super().setUp()

        self.url = "/api/partner"

    @odoo.tools.mute_logger("odoo.addons.auth_api_key.models.ir_http")
    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_raise_error_without_auth(self):
        response = self.http_get_without_auth()

        self.assertEquals(response.status_code, 403)
        self.assertEquals(response.reason, "FORBIDDEN")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_without_ref(self):
        response = self.http_get(self.url)

        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.reason, "BAD REQUEST")

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_get_not_found(self):
        response = self.http_get(
            "{}/{}".format(self.url, 123)
        )

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.reason, "NOT FOUND")

    def test_route_get(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")

        response = self.http_get(
            "{}/{}".format(self.url, int(partner.ref))
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(content["id"], partner.id)
        self.assertEqual(content["name"], partner.name)
        self.assertEqual(content["ref"], partner.ref)
        self.assertEqual(content["addresses"][0]["street"], partner.street)
        self.assertEqual(
            content["cooperator_register_number"],
            partner.cooperator_register_number
        )
        self.assertEqual(
            content["cooperator_end_date"],
            ""
        )
        self.assertEqual(
            content['sponsorship_code'], partner.sponsorship_hash
        )
        self.assertEqual(content['sponsees_number'], 1)
        self.assertEqual(
            content['sponsees_max'], partner.company_id.max_sponsees_number
        )
        self.assertEqual(
            content['sponsorship_code'], partner.sponsorship_hash
        )

    def test_route_get_with_active_provisioning(self):
        partner = self.browse_ref('somconnexio.res_sponsored_partner_1_demo')
        sponsor = partner.sponsor_id
        self.assertFalse(partner.contract_ids)
        self.assertEquals(sponsor.sponsee_ids, partner)
        crm_lead_id = self.env['crm.lead'].create(
            [{
                'name': 'Test Lead',
                'partner_id': partner.id,
            }]
        )[0].id
        broadband_isp_info = self.env['broadband.isp.info'].create({
            'phone_number': '666666666',
            'type': 'new',
        })
        broadband_adsl_product_tmpl_args = {
            'name': 'ADSL 20Mb',
            'type': 'service',
            'categ_id': self.ref('somconnexio.broadband_adsl_service')
        }
        product_adsl_broadband_tmpl = self.env['product.template'].create(
            broadband_adsl_product_tmpl_args
        )
        product_broadband_adsl = product_adsl_broadband_tmpl.product_variant_id

        ticket_number = "1234"
        crm_lead_line_args = {
            'lead_id': crm_lead_id,
            'broadband_isp_info': broadband_isp_info.id,
            'product_id': product_broadband_adsl.id,
            'name': '666666666',
            'ticket_number': ticket_number,
        }
        self.env['crm.lead.line'].create(
            [crm_lead_line_args]
        )
        self.assertTrue(partner.has_lead_in_provisioning)
        response = self.http_get(
            "{}/{}".format(self.url, int(sponsor.ref))
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(content['sponsees_number'], 2)

    def test_route_get_with_active_sponsees(self):

        self.Contract = self.env['contract.contract']
        self.product_1 = self.env.ref('product.product_product_1')
        self.router_product = self.env['product.product'].search(
            [
                ("default_code", "=", "NCDS224WTV"),
            ]
        )
        self.router_lot = self.env['stock.production.lot'].create({
            'product_id': self.router_product.id,
            'name': '123',
            'router_mac_address': '12:BB:CC:DD:EE:90'
        })
        self.mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'icc': '123'
        })
        self.adsl_contract_service_info = self.env[
            'adsl.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'administrative_number': '123',
            'router_product_id': self.router_product.id,
            'router_lot_id': self.router_lot.id,
            'ppp_user': 'ringo',
            'ppp_password': 'rango',
            'endpoint_user': 'user',
            'endpoint_password': 'password'
        })
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.partner = self.browse_ref('somconnexio.res_sponsored_partner_1_demo')
        self.service_partner = self.env['res.partner'].create({
            'parent_id': self.partner.id,
            'name': 'Service partner',
            'type': 'service'
        })
        vals_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': self.partner.id,
            'service_partner_id': self.service_partner.id,
            'invoice_partner_id': self.partner.id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_fiber"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_vodafone"
            ),
            'vodafone_fiber_service_contract_info_id': (
                self.vodafone_fiber_contract_service_info.id
            ),
            'bank_id': self.partner.bank_ids.id
        }
        self.assertTrue(self.env['contract.contract'].create(vals_contract))
        sponsor = self.browse_ref("somconnexio.res_partner_1_demo")
        response = self.http_get(
            "{}/{}".format(self.url, int(sponsor.ref))
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content['sponsees_number'], 2)

    @odoo.tools.mute_logger("odoo.addons.base_rest.http")
    def test_route_search_not_found(self):
        response = self.http_get(
            "{}?vat={}".format(self.url, "66758531L")
        )

        self.assertEquals(response.status_code, 404)
        self.assertEquals(response.reason, "NOT FOUND")

    def test_route_search(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")

        response = self.http_get(
            "{}?vat={}".format(self.url, partner.vat)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(content["id"], partner.id)
        self.assertEqual(content["name"], partner.name)
        self.assertEqual(content["ref"], partner.ref)
        self.assertEqual(
            content["cooperator_register_number"],
            partner.cooperator_register_number
        )
        self.assertEqual(
            content["cooperator_end_date"],
            ""
        )
        self.assertFalse(content["coop_candidate"])
        self.assertTrue(content["member"])

    def test_route_search_normalize_vat(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")

        bad_formatted_vat = "  {}---. ".format(partner.vat)
        response = self.http_get(
            "{}?vat={}".format(self.url, bad_formatted_vat)
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(content["id"], partner.id)

    def test_filter_duplicate_addresses(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")
        address_dict = {
            'type': 'service',
            'parent_id': partner.id,
            'street': 'test',
            'street2': 'test',
            'zip': '08123',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'name': 'test',
        }
        address_dict['street'] = 'Test'
        self.env['res.partner'].create(address_dict)
        address_dict['street'] = '  Test '
        self.env['res.partner'].create(address_dict)

        response = self.http_get(
            "{}/{}".format(self.url, int(partner.ref))
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.reason, "OK")

        content = json.loads(response.content.decode("utf-8"))

        self.assertEqual(content["id"], partner.id)
        self.assertEqual(len(content["addresses"]), 2)

    def test_can_sponsor_ok(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")

        route = "{url}?vat={vat}&sponsor_code={sponsor_code}".format(
            url=self.url + "/check_sponsor",
            vat=partner.vat,
            sponsor_code=partner.sponsorship_hash,
        )
        content = self.http_get_content(route)

        self.assertEqual(content["result"], "allowed")
        self.assertEqual(content["message"], "ok")

    def test_can_sponsor_ok_code_insensitive(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")

        route = "{url}?vat={vat}&sponsor_code={sponsor_code}".format(
            url=self.url + "/check_sponsor",
            vat=partner.vat,
            sponsor_code=partner.sponsorship_hash.upper(),
        )
        content = self.http_get_content(route)

        self.assertEqual(content["result"], "allowed")
        self.assertEqual(content["message"], "ok")

    def test_can_sponsor_ko_maximum_exceeded(self):
        partner = self.browse_ref("somconnexio.res_partner_1_demo")
        while(partner.active_sponsees_number < partner.company_id.max_sponsees_number):
            sr_vals = subscription_request_create_data(self)
            sr_vals.update({'sponsor_id': partner.id})
            self.assertTrue(self.env['subscription.request'].create(sr_vals))

        route = "{url}?vat={vat}&sponsor_code={sponsor_code}".format(
            url=self.url + "/check_sponsor",
            vat=partner.vat,
            sponsor_code=partner.sponsorship_hash,
        )
        content = self.http_get_content(route)

        self.assertEqual(content["result"], "not_allowed")
        self.assertEqual(content["message"], "maximum number of sponsees exceeded")

    def test_can_sponsor_ko_invalid_code_or_vat(self):
        route = "{url}?vat={vat}&sponsor_code={sponsor_code}".format(
            url=self.url + "/check_sponsor",
            vat="WRONG VAT",
            sponsor_code="WRONG SPONSOR CODE"
        )
        content = self.http_get_content(route)

        self.assertEqual(content["result"], "not_allowed")
        self.assertEqual(content["message"], "invalid code or vat number")
