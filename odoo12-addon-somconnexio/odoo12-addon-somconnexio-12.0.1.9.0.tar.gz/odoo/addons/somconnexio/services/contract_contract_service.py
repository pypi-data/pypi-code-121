from odoo.exceptions import MissingError
from odoo import _


class ContractService:
    def __init__(self, env):
        self.env = env
        self.Contract = self.env['contract.contract']

    def search(self, **params):
        code = params.get('code')
        phone_number = params.get('phone_number')
        partner_vat = params.get('partner_vat')

        if code:
            contracts = self.Contract.sudo().search(
                [('code', '=', code)]
            )
            search_param = 'code'
        elif phone_number:
            contracts = self.Contract.sudo().search(
                [('phone_number', '=', phone_number)]
            )
            search_param = 'phone_number'
        elif partner_vat:
            partner = self.env['res.partner'].sudo().search([
                ('vat', '=', partner_vat),
                ('parent_id', '=', False)
            ])
            contracts = self.Contract.sudo().search(
                [('partner_id', '=', partner.id)]
            )
            search_param = 'partner_vat'
        if not contracts:
            raise MissingError(
                _('No contract with {}: {} could be found'.format(
                    search_param, params.get(search_param)))
                )

        return [self._to_dict(contract) for contract in contracts]

    def create(self, **params):
        self.Contract.with_delay().create_contract(**params)
        return {"result": "OK"}

    def count(self):
        domain_contracts = [('is_terminated', '=', False)]
        domain_members = [
            ('parent_id', '=', False), ('customer', '=', True),
            '|', ('member', '=', True), ('coop_candidate', '=', True)
        ]
        number = self.Contract.sudo().search_count(domain_contracts)
        result = {"contracts": number}
        number = self.env['res.partner'].sudo().search_count(domain_members)
        result['members'] = number
        return result

    def _to_dict(self, contract):
        contract.ensure_one()

        return {
            "id": contract.id,
            "code": contract.code,
            "customer_firstname": contract.partner_id.firstname,
            "customer_lastname": contract.partner_id.lastname,
            "customer_ref": contract.partner_id.ref,
            "customer_vat": contract.partner_id.vat,
            "phone_number": contract.phone_number,
            "current_tariff_product": contract.current_tariff_product.default_code,
            "ticket_number": contract.ticket_number,
            "technology": contract.service_technology_id.name,
            "supplier": contract.service_supplier_id.name,
            "lang": contract.lang,
            "iban": contract.mandate_id.partner_bank_id.sanitized_acc_number,
            "is_terminated": contract.is_terminated,
            "date_start": contract.date_start,
            "date_end": contract.date_end,
        }
