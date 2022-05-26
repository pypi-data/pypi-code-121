import logging

from odoo.exceptions import UserError
from odoo import _
from . import schemas
try:
    from cerberus import Validator
except ImportError:
    _logger = logging.getLogger(__name__)
    _logger.debug("Can not import cerberus")

_logger = logging.getLogger(__name__)


class PartnerEmailChangeProcess:
    _description = """
        Run Partner Email Change Wizard from API
    """

    def __init__(self, env=False):
        self.env = env

    def run_from_api(self, **params):
        _logger.info(
            "Starting process to change partner email with body: {}".format(params)
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
        ret = {
            'partner_id': partner.id,
            'email_id': email_id,
            'change_contact_email': "yes",
            'change_contracts_emails': "no",
        }
        return ret

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
        return schemas.S_PARTNER_EMAIL_CHANGE_CREATE

    @staticmethod
    def to_dict(wiz):
        return {'wiz_id': wiz.id}
