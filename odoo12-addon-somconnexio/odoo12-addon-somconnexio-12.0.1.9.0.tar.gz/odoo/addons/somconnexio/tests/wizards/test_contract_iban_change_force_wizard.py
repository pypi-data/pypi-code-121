from mock import patch, Mock
from ..sc_test_case import SCTestCase


class TestContractIBANChangeForceWizard(SCTestCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Contract = self.env['contract.contract']
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.partner = self.browse_ref('base.partner_demo')
        partner_id = self.partner.id
        service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        self.bank_b = self.env['res.partner.bank'].create({
            'acc_number': 'ES1720852066623456789011',
            'partner_id': partner_id
        })
        self.banking_mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': self.bank_b.id,
        })
        vals_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': service_partner.id,
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
            'mandate_id': self.banking_mandate.id
        }
        self.contract = self.env['contract.contract'].create(vals_contract)
        self.user_admin = self.browse_ref('base.user_admin')

    @patch(
        'odoo.addons.somconnexio.models.contract.CRMAccountHierarchyFromContractUpdateService',  # noqa
        return_value=Mock(spec=["run"])
    )
    def test_wizard_iban_change_ok(self, MockUpdateService):
        wizard = self.env['contract.iban.change.force.wizard'].with_context(
            active_id=self.partner.id
        ).sudo(
            self.user_admin
        ).create({
            'contract_ids': [(6, 0, [
                self.contract.id
            ])],
            'account_banking_mandate_id': self.banking_mandate.id
        })
        self.assertFalse('start_date' in dir(wizard))
        partner_activities_before = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)]
        )
        wizard.button_change()
        self.assertEquals(self.contract.mandate_id, self.banking_mandate)

        MockUpdateService.assert_called_once_with(
            wizard.contract_ids,
            "iban",
            force=True
        )
        MockUpdateService.return_value.run.assert_called_once_with()

        partner_activities_after = self.env['mail.activity'].search(
            [('partner_id', '=', self.partner.id)],
        )
        self.assertEquals(len(partner_activities_after) -
                          len(partner_activities_before), 1)

        created_activity = partner_activities_after[-1]
        self.assertEquals(created_activity.user_id, self.user_admin)
        self.assertEquals(created_activity.summary, 'IBAN change')
        self.assertEquals(
            created_activity.activity_type_id,
            self.browse_ref('somconnexio.mail_activity_type_iban_change')
        )
        self.assertEquals(created_activity.done, True)
