import os
import json

from hashflow.constants import ZERO_ADDRESS


class Factory(object):

    def __init__(
        self,
        main,
    ):
        self.main = main

        # initialize contracts
        self.factory = self.main.create_hashflow_contract(
            'HashflowFactory',
            self.main.network_id
        )
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
        self.governance_address = \
            deployed_addresses['HashflowGovernance'][str(self.main.network_id)]['address']
    
    def test(
        self,
        options=None
    ):
        '''
        Test connection with the network.
        '''
        result = self.factory.functions.test().call()
        return result

    def create_pool(
        self,
        name,
        signer,
        symbol=None,
        privPool=True,
        options=None
    ):
        '''
        Allows market makers to create a pool.
        '''
        return self.main.send_eth_transaction(
            method=self.factory.functions.createPool(
                name,
                symbol or '',
                self.main.web3.toChecksumAddress(signer),
                privPool,
            ),
            options=options
        )

    
    def get_pools(
        self,
        operations,
    ):
        '''
        Query all pool addresses deployed using the operations key. 
        '''
        result = self.factory.functions.getPools(
            self.main.web3.toChecksumAddress(operations),
        ).call()

        return result

    
