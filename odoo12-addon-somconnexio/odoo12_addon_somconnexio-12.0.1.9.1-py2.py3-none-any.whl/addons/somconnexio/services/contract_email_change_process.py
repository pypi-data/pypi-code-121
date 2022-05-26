import logging

from datetime import date
from odoo.exceptions import UserError
from odoo import _
from . import schemas
try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")

_logger = logging.getLogger(__name__)


class ContractEmailChangeProcess:
    _description = """
        Run Partner Email Change Wizard from API
    """

    def __init__(self, env=False):
        self.env = env

    def run_from_api(self, **params):
        _logger.info(
            "Starting process to change contracts' email with body: {}".format(params)
        )
        v = Validator(purge_unknown=True)
        if not v.validate(params, self.validator_create(),):
            raise UserError(_('BadRequest {}').format(v.errors))
        params = self._prepare_create(params)
        wiz = self.env["partner.email.change.wizard"].with_context(
            active_id=params['partner_id']
        ).sudo().create(params)
        wiz.button_change()
        return self.to_dict(wiz)

    def _prepare_create(self, params):
        partner = self.env['res.partner'].sudo().search(
            [
                ("ref", "=", params['partner_id']),
            ]
        )
        if not partner:
            raise UserError(
                _('Partner id %s not found') % (params['partner_id'],)
            )
        email_id = self._prepare_email_id(params, partner)
        contract_ids = self._prepare_contract_ids(params, partner.id)
        ret = {
            'partner_id': partner.id,
            'email_id': email_id,
            'change_contact_email': "no",
            'change_contracts_emails': 'yes',
            'contract_ids': contract_ids,
        }
        return ret

    def _prepare_contract_ids(self, params, partner_id):
        contracts = params.get('contracts')
        if contracts:
            if type(contracts) != str:
                raise UserError("Contracts must be string or empty dict")
            contract_ids = []
            for contract_ref in contracts.split(";"):
                contract_id = self.env['contract.contract'].sudo().search([
                    ('partner_id', '=', partner_id),
                    ('code', '=', contract_ref)
                ]).id
                if not contract_id:
                    raise UserError(
                        _('Contract %s not found for partner %s') % (
                            contract_ref, partner_id
                        )
                    )
                contract_ids.append(contract_id)
        else:
            contract_ids = self.env['contract.contract'].sudo().search([
                ('partner_id', '=', partner_id),
                '|',
                ('date_end', '>', date.today().strftime('%Y-%m-%d')),
                ('date_end', '=', False)
            ]).ids
        return [(6, 0, contract_ids)]

    def _prepare_email_id(self, params, partner):
        email = params['email']
        email_partner = self.env['res.partner'].sudo().search([
            ('parent_id', '=', partner.id),
            ('email', '=', email),
            ('type', '=', 'contract-email')
        ])
        if not email_partner:
            email_partner = self._create_email_partner(partner, email)
        return email_partner.id

    def _create_email_partner(self, partner, email):
        return self.env['res.partner'].sudo().create({
            'parent_id': partner.id,
            'type': 'contract-email',
            'email': email,
        })

    @staticmethod
    def validator_create():
        return schemas.S_CONTRACT_EMAIL_CHANGE_CREATE

    @staticmethod
    def to_dict(wiz):
        return {'wiz_id': wiz.id}
