from odoo import SUPERUSER_ID, api

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Contract = env["contract.contract"]
    CrmLeadLine = env["crm.lead.line"]
    crm_lead_lines = CrmLeadLine.search([('ticket_number', '!=', False)])

    for crm_lead_line in crm_lead_lines:
        contracts = Contract.search([
            ('ticket_number', '=', crm_lead_line.ticket_number)
        ])
        if len(contracts) == 0:
            _logger.info(
                "There is no contract with ticket number {}".format(
                    crm_lead_line.ticket_number)
            )
        elif len(contracts) > 1:
            _logger.info(
                "There are {} contracts with ticket number {}".format(
                    len(contracts), crm_lead_line.ticket_number)
            )
        else:
            contract = contracts[0]
            contract.write({"crm_lead_line_id": crm_lead_line.id})
