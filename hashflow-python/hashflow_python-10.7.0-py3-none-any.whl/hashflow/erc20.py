import os
import json

from hashflow.constants import MAX_SOLIDITY_UINT

class ERC20(object):

    def __init__(
        self,
        main
    ):
        self.main = main
        this_folder = os.path.dirname(os.path.abspath(__file__))

        deployed_file_path = os.path.join(
            this_folder,
            'deployed.json'
        )
        deployed_addresses = json.load(
            open(deployed_file_path, 'r')
        )

        self.router_address = \
            deployed_addresses['HashflowRouter'][str(self.main.network_id)]['address']

    # -----------------------------------------------------------
    # Transactions
    # -----------------------------------------------------------

    def allowance(
        self,
        token,
        owner,
        spender,
    ):
        contract = self.main.create_contract(
            'IERC20',
            self.main.web3.toChecksumAddress(token),
        )

        result = contract.functions.allowance(
            self.main.web3.toChecksumAddress(owner),
             self.main.web3.toChecksumAddress(spender),
        ).call()

        return result

    def totalSupply(
        self,
        token,
    ):
        contract = self.main.create_contract(
            'IERC20',
            token,
        )

        result = contract.functions.totalSupply().call()

        return result

    def name(
        self,
        token,
    ):
        contract = self.main.create_contract(
            'IERC20',
            token,
        )

        result = contract.functions.name().call()

        return result


    def symbol(
        self,
        token,
    ):
        contract = self.main.create_contract(
            'IERC20',
            token,
        )

        result = contract.functions.symbol().call()

        return result

    def decimals(
        self,
        token,
    ):
        contract = self.main.create_contract(
            'IERC20',
            token,
        )

        result = contract.functions.decimals().call()

        return result

    def set_maximum_hashflow_allowance(
        self,
        token,
        options=None
    ):
        contract = self.main.create_contract(
            'IERC20',
            token,
        )
        return self.main.send_eth_transaction(
            method=contract.functions.approve(
                self.router_address,
                MAX_SOLIDITY_UINT
            ),
            options=options
        )


    def unset_allowance(
        self,
        token,
        options=None
    ):
        contract = self.main.create_contract(
            'IERC20',
            token,
        )
        return self.main.send_eth_transaction(
            method=contract.functions.approve(
                self.router_address,
                0,
            ),
            options=options
        )

    
    def transfer(
        self,
        token,
        receiver,
        amount,
        options=None
    ):
        contract = self.main.create_contract(
            'IERC20',
            token,
        )
        return self.main.send_eth_transaction(
            method=contract.functions.transfer(
                self.main.web3.toChecksumAddress(receiver),
                amount,
            ),
            options=options
        )

    def transfer_from(
        self,
        token,
        spender,
        receiver,
        amount,
        options=None
    ):
        contract = self.main.create_contract(
            'IERC20',
            token,
        )
        return self.main.send_eth_transaction(
            method=contract.functions.transferFrom(
                self.main.web3.toChecksumAddress(spender),
                self.main.web3.toChecksumAddress(receiver),
                amount,
            ),
            options=options
        )

