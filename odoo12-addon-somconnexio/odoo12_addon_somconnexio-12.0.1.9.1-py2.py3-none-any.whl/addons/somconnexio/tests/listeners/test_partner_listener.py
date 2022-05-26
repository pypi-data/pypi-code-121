import os
from mock import patch, Mock
from datetime import date, timedelta

from ..sc_test_case import SCComponentTestCase


@patch.dict(os.environ, {
    'SOMOFFICE_URL': 'https://somoffice.coopdevs.org/',
})
@patch('odoo.addons.somconnexio.somoffice.user.requests', spec=['request'])
class TestPartnerListener(SCComponentTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestPartnerListener, cls).setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(context=dict(
            cls.env.context,
            tracking_disable=True,
            test_queue_job_no_delay=False,
        ))

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner = self.browse_ref('somconnexio.res_partner_2_demo')
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '999990999',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        partner_id = self.partner.id
        self.service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        self.ba_contract = self.env['contract.contract'].create({
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': self.service_partner.id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_fiber"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_vodafone"
            ),
            'vodafone_fiber_service_contract_info_id': (
                self.vodafone_fiber_contract_service_info.id
            ),
        })

    def test_create_user_if_customer_and_cooperator(self, mock_requests):
        mock_requests.request.return_value = Mock(spec=['status_code', 'json'])
        mock_requests.request.return_value.status_code = 200

        queue_jobs_before = self.env['queue.job'].search_count([])

        self.env['res.partner'].create({
            'parent_id': None,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'cooperator': True,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })

        queue_jobs_after = self.env['queue.job'].search_count([])

        self.assertEqual(queue_jobs_before, queue_jobs_after-1)

    def test_not_create_user_if_not_customer_and_cooperator(self, mock_requests):
        mock_requests.request.return_value = Mock(spec=['status_code', 'json'])
        mock_requests.request.return_value.status_code = 200

        queue_jobs_before = self.env['queue.job'].search_count([])

        self.env['res.partner'].create({
            'parent_id': None,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': False,
            'cooperator': True,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })

        queue_jobs_after = self.env['queue.job'].search_count([])

        self.assertEqual(queue_jobs_before, queue_jobs_after)

    def test_not_create_user_if_not_customer_and_not_cooperator(self, mock_requests):
        mock_requests.request.return_value = Mock(spec=['status_code', 'json'])
        mock_requests.request.return_value.status_code = 200

        queue_jobs_before = self.env['queue.job'].search_count([])

        self.env['res.partner'].create({
            'parent_id': None,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': False,
            'cooperator': False,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })

        queue_jobs_after = self.env['queue.job'].search_count([])

        self.assertEqual(queue_jobs_before, queue_jobs_after)

    def test_not_create_user_if_partner_already_exists(self, mock_requests):
        mock_requests.request.return_value = Mock(spec=['status_code', 'json'])
        mock_requests.request.return_value.status_code = 200

        queue_jobs_before = self.env['queue.job'].search_count([])

        self.env['res.partner'].create({
            'parent_id': self.partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'cooperator': False,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })

        queue_jobs_after = self.env['queue.job'].search_count([])

        self.assertEqual(queue_jobs_before, queue_jobs_after)

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_sell_back_member_without_sponsees(self, send_mail_mock, _):
        self.partner.member = False
        send_mail_mock.assert_not_called()

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_sell_back_member_with_sponsees(self, send_mail_mock, _):
        sponsee = self.env['res.partner'].create({
            'sponsor_id': self.partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'cooperator': False,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })
        self.ba_contract.write({
            'partner_id': sponsee.id,
            'invoice_partner_id': sponsee.id,
            'service_partner_id': sponsee.id,
        })
        self.partner.write({'member': False})
        send_mail_mock.assert_called()

    @patch('odoo.addons.mail.models.mail_template.MailTemplate.send_mail')
    def test_sell_back_member_with_sponsees_terminated_contract(self, send_mail_mock, _): # noqa
        sponsee = self.env['res.partner'].create({
            'sponsor_id': self.partner.id,
            'name': 'test',
            'street': 'test',
            'street2': 'test',
            'city': 'city',
            'state_id': self.ref('base.state_es_b'),
            'country_id': self.ref('base.es'),
            'customer': True,
            'cooperator': False,
            'email': 'test@example.com',
            'lang': 'ca_ES',
        })
        self.ba_contract.write({
            'partner_id': sponsee.id,
            'invoice_partner_id': sponsee.id,
            'service_partner_id': sponsee.id,
            'date_end': date.today() - timedelta(days=1)
        })
        self.partner.write({'member': False})
        send_mail_mock.assert_not_called()
