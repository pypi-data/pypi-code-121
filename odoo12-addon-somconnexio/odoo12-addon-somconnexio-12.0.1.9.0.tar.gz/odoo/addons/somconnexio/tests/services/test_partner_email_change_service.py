from mock import patch, Mock, ANY
import odoo
import json
from odoo.addons.easy_my_coop_api.tests.common import BaseEMCRestCase
from odoo.exceptions import UserError
from ...somoffice.errors import SomOfficeUserChangeEmailError
from ...services.partner_email_change_process import PartnerEmailChangeProcess

HOST = "127.0.0.1"
PORT = odoo.tools.config["http_port"]


class BaseEMCRestCaseAdmin(BaseEMCRestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        # Skip parent class in super to avoid recreating api key
        super(BaseEMCRestCase, cls).setUpClass(*args, **kwargs)
        cls.env = cls.env(context=dict(
            cls.env.context,
            tracking_disable=True,  # no jobs thanks
        ))


class TestPartnerEmailChangeService(BaseEMCRestCaseAdmin):
    def setUp(self, *args, **kwargs):
        super().setUp()
        self.partner = self.browse_ref('base.partner_demo')
        self.partner.ref = "1234test"
        self.partner_ref = self.partner.ref
        self.email = "test@example.org"
        self.ResPartner = self.env['res.partner']
        self.partner_email_b = self.ResPartner.create({
            'name': 'Email b',
            'email': self.email,
            'type': 'contract-email',
            'parent_id': self.partner.id
        })
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })

    def http_public_post(self, url, data, headers=None):
        if url.startswith("/"):
            url = "http://{}:{}{}".format(HOST, PORT, url)
        return self.session.post(url, json=data)

    @patch(
        'odoo.addons.somconnexio.wizards.partner_email_change.partner_email_change.ChangePartnerEmails',  # noqa
        return_value=Mock(spec=[
            "change_contact_email",
            "change_somoffice_email"
        ])
    )
    def test_route_right_run_wizard_contact_email_change(self, MockChangePartnerEmails):
        url = "/public-api/partner-email-change"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = PartnerEmailChangeProcess(self.env)
        process.run_from_api(**data)
        MockChangePartnerEmails.assert_called_once_with(
            ANY,
            self.partner
        )
        MockChangePartnerEmails.return_value.change_contact_email.assert_called_once_with(  # noqa
            self.partner_email_b,
        )
        MockChangePartnerEmails.return_value.change_somoffice_email.assert_called_once_with(  # noqa
            self.partner_email_b,
        )

    @patch(
        'odoo.addons.somconnexio.wizards.partner_email_change.partner_email_change.ChangePartnerEmails',  # noqa
        return_value=Mock(spec=[
            "change_contact_email",
            "change_somoffice_email"
        ])
    )
    def test_route_bad_run_wizard_contact_email_fail(
        self, MockChangePartnerEmails
    ):
        MockChangePartnerEmails.return_value.change_somoffice_email.side_effect = SomOfficeUserChangeEmailError(self.partner.ref, "Error Text")  # noqa
        url = "/public-api/partner-email-change"
        data = {
            "partner_id": self.partner_ref,
            "email": self.email,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = PartnerEmailChangeProcess(self.env)
        self.assertRaises(
            UserError,
            process.run_from_api,
            **data
        )

    def test_route_bad_run_wizard_missing_partner_id(self):
        url = "/public-api/partner-email-change"
        data = {
            "email": self.email,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = PartnerEmailChangeProcess(self.env)
        self.assertRaises(
            UserError,
            process.run_from_api,
            **data
        )

    def test_route_bad_run_wizard_missing_email(self):
        url = "/public-api/partner-email-change"
        data = {
            "partner_id": self.partner_ref,
            "change_contracts_emails": False,
            "change_contact_email": True,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = PartnerEmailChangeProcess(self.env)
        self.assertRaises(
            UserError,
            process.run_from_api,
            **data
        )

    def test_route_bad_run_wizard_partner_id_not_found(self):
        url = "/public-api/partner-email-change"
        data = {
            "partner_id": 'XXX',
            "email": self.email,
            "change_contracts_emails": False,
            "change_contact_email": True,
        }
        response = self.http_public_post(url, data=data)
        self.assertEquals(response.status_code, 200)
        decoded_response = json.loads(response.content.decode("utf-8"))
        self.assertEquals(decoded_response, {"result": "OK"})
        process = PartnerEmailChangeProcess(self.env)
        self.assertRaises(
            UserError,
            process.run_from_api,
            **data
        )
