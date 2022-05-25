from odoo import SUPERUSER_ID, api

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Contract = env["contract.contract"]
    reason_holder_change_id = env.ref('somconnexio.reason_holder_change').id
    holder_change_contracts = Contract.search([
        ('terminate_reason_id', '=', reason_holder_change_id)
    ])
    for old_contract in holder_change_contracts:
        active_contract = Contract.search([
            ('is_terminated', '=', False),
            '|', '|', '|', '|', '|',
            ('vodafone_fiber_service_contract_info_id.id', '=', old_contract.vodafone_fiber_service_contract_info_id.id),  # noqa
            ('mm_fiber_service_contract_info_id.id', '=', old_contract.mm_fiber_service_contract_info_id.id),  # noqa
            ('orange_fiber_service_contract_info_id.id', '=', old_contract.orange_fiber_service_contract_info_id.id),  # noqa
            ('router_4G_service_contract_info_id.id', '=', old_contract.router_4G_service_contract_info_id.id),  # noqa
            ('adsl_service_contract_info_id.id', '=', old_contract.adsl_service_contract_info_id.id),  # noqa
            ('xoln_fiber_service_contract_info_id.id', '=', old_contract.xoln_fiber_service_contract_info_id.id),  # noqa
        ])
        if old_contract.vodafone_fiber_service_contract_info_id:
            active_contract.write({
                'vodafone_fiber_service_contract_info_id': old_contract.vodafone_fiber_service_contract_info_id.copy().id  # noqa
            })
        elif old_contract.mm_fiber_service_contract_info_id:
            active_contract.write({
                'mm_fiber_service_contract_info_id': old_contract.mm_fiber_service_contract_info_id.copy().id  # noqa
            })
        elif old_contract.orange_fiber_service_contract_info_id:
            active_contract.write({
                'orange_fiber_service_contract_info_id': old_contract.orange_fiber_service_contract_info_id.copy().id  # noqa
            })
        elif old_contract.router_4G_service_contract_info_id:
            active_contract.write({
                'router_4G_service_contract_info_id': old_contract.router_4G_service_contract_info_id.copy().id  # noqa
            })
        elif old_contract.xoln_fiber_service_contract_info_id:
            active_contract.write({
                'xoln_fiber_service_contract_info_id': old_contract.xoln_service_contract_info_id.copy().id  # noqa
            })
        elif old_contract.adsl_service_contract_info_id:
            active_contract.write({
                'adsl_service_contract_info_id': old_contract.adsl_service_contract_info_id.copy().id  # noqa
            })
