from odoo.addons.component.core import Component
from datetime import date


class Partner(Component):
    _name = 'partner.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['res.partner']

    def on_record_create(self, record, fields=None):
        # Early return if is not a Contact(is the parent)
        if record.parent_id:
            return
        if record.customer and record.cooperator:
            self.env['res.partner'].with_delay().create_user(record)

    def on_record_write(self, record, fields=None):
        if 'member' in fields and record.member is False:
            for sponsee in record.sponsee_ids:
                has_active_contracts = any(
                    not (contract.date_end and contract.date_end < date.today())
                    for contract in sponsee.contract_ids
                )
                if has_active_contracts:
                    template = self.env.ref('somconnexio.sponsor_sell_back_template')
                    template.send_mail(sponsee.id)

        address_fields = ['street',  'street2', 'zip', 'city', 'state_id', 'country_id']
        is_address_edited = any(True for field in fields if field in address_fields)
        if is_address_edited and record.contract_ids:
            record.with_delay().update_accounts_address()
            record.with_delay().update_customer()
