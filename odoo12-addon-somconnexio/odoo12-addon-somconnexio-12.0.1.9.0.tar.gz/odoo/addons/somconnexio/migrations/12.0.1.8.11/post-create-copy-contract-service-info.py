from odoo import SUPERUSER_ID, api

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info("Compute sponsorship hash for the existent coop_candidates start")  # noqa
    partners = env["res.partner"].search([('coop_candidate', '=', True)])
    partners._compute_sponsorship_hash()
    _logger.info("Compute sponsorship hash ends")
