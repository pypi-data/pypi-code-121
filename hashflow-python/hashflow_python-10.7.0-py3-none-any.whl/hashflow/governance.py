from hashflow.constants import ZERO_ADDRESS
from hashflow.util import Trade, Flag


class Governance(object):

    def __init__(
        self,
        main,
    ):
        self.main = main

        # initialize contracts
        self.governance = self.main.create_hashflow_contract(
            'HashflowGovernance',
            self.main.network_id
        )

    def set_withdrawal_period(
        self,
        withdrawal_period,
        options=None,
    ):

        return self.main.send_eth_transaction(
            method=self.governance.functions.setWithdrawPeriod(
                withdrawal_period
            ),
            options=options
        )

    def set_percent_withdrawal_limit(
        self,
        percent_withdrawal_limit,
        options=None,
    ):

        return self.main.send_eth_transaction(
            method=self.governance.functions.setPercentWithdrawLimit(
                percent_withdrawal_limit
            ),
            options=options
        )

    def update_router_auth_status(
        self,
        router,
        status,
        options=None,
    ):

        return self.main.send_eth_transaction(
            method=self.governance.functions.updateRouterAuthStatus(
                router,
                status,
            ),
            options=options
        )
    
    def get_withdrawal_period(
        self,
        options=None,
    ):

        return self.main.send_eth_transaction(
            method=self.governance.functions.getWithdrawPeriod(
            ),
            options=options
        )

    def get_percent_withdrawal_limit(
        self,
        options=None,
    ):

        return self.main.send_eth_transaction(
            method=self.governance.functions.getPercentWithdrawLimit(
            ),
            options=options
        )

    def router_authorized(
        self,
        options=None,
    ):

        return self.main.send_eth_transaction(
            method=self.governance.functions.getRouterAuthStatus(
            ),
            options=options
        )

    
