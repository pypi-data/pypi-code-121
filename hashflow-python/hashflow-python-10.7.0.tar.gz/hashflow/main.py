import json
import os
import time
from web3 import Web3
import hashflow.constants as consts
from hashflow.factory import Factory
from hashflow.router import Router
from hashflow.governance import Governance
from hashflow.erc20 import ERC20
from hashflow.pool import Pool
from hashflow.util import Flag


class Main(object):

    def __init__(
        self,
        node,
        private_key,
        public_address,
        network_id
    ):
        self.web3 = Web3(None if node is None else Web3.HTTPProvider(node))
        self.private_key = private_key
        self.public_address = public_address
        self.min_nonce = self.web3.eth.getTransactionCount(self.public_address)
        self.network_id = network_id

        self.factory = Factory(self)
        self.router = Router(self)
        self.governance = Governance(self)
        self.erc20 = ERC20(self)
        self.pool = Pool(self)

    def send_native_token(self, to, amount, options=None):
        if options is None:
            options = dict()
        tx = {
            'from': self.public_address,
            'nonce': self.web3.eth.getTransactionCount(self.public_address),
            'to': self.web3.toChecksumAddress(to),
            'value': amount,
            'gas': 2000000,
            'chainId': self.network_id
        }
        if 'gasPrice' in options:
            tx['gasPrice'] = options['gasPrice']
        if 'maxFeePerGas' in options:
            tx['maxFeePerGas'] = options['maxFeePerGas']
        if 'maxPriorityFeePerGas' in options:
            tx['maxPriorityFeePerGas'] = options['maxPriorityFeePerGas']

        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)

        return self.web3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()


    # -----------------------------------------------------------
    # Helper Functions
    # -----------------------------------------------------------

    def send_eth_transaction(
        self,
        method,
        options=None
    ):
        if options is None:
            options = dict()
        if 'from' not in options:
            options['from'] = self.public_address
        if 'nonce' not in options:
            options['nonce'] = max(
                self.min_nonce,
                self.web3.eth.getTransactionCount(self.public_address)
            )
        if 'gasPrice' not in options:
            if 'maxFeePerGas' not in options:
                options['maxFeePerGas'] = consts.DEFAULT_MAX_GAS_FEE

            if 'maxPriorityFeePerGas' not in options:
                options['maxPriorityFeePerGas'] = consts.DEFAULT_MAX_PRIORITY_FEE
        # if 'gasPrice' not in options:
        #     try:
        #         options['gasPrice'] = \
        #             self.web3.eth.gasPrice + consts.DEFAULT_GAS_PRICE_ADDITION
        #     except Exception:
        #         options['gasPrice'] = consts.DEFAULT_GAS_PRICE
        if 'value' not in options:
            options['value'] = 0
        if 'gas' not in options:
            try:
                options['gas'] = int(
                    method.estimateGas(options) *
                    consts.DEFAULT_GAS_MULTIPLIER
                )
            except Exception:
                options['gas'] = consts.DEFAULT_GAS_AMOUNT
        self.min_nonce = max(self.min_nonce, options['nonce'] + 1)
        tx = method.buildTransaction(options)
        signed_tx = self.web3.eth.account.sign_transaction(
            tx, self.private_key)
        return self.web3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

    def create_hashflow_contract(
        self,
        name,
        network_id
    ):
        this_folder = os.path.dirname(os.path.abspath(__file__))
        abi_file_path = os.path.join(
            this_folder,
            'abi/I{}.json'.format(name)
        )
        deployed_file_path = os.path.join(
            this_folder,
            'deployed.json'
        )
        deployed_addresses = json.load(
            open(deployed_file_path, 'r')
        )
        contract_address = deployed_addresses[name][str(network_id)]['address']
        return self.web3.eth.contract(
            address=contract_address,
            abi=json.load(open(abi_file_path, 'r'))
        )

    def create_contract(
        self,
        name,
        address
    ):
        this_folder = os.path.dirname(os.path.abspath(__file__))
        abi_file_path = os.path.join(
            this_folder,
            'abi/{}.json'.format(name)
        )
        return self.web3.eth.contract(
            address=address,
            abi=json.load(open(abi_file_path, 'r'))
        )

    def get_receipt(
        self,
        tx_hash
    ):
        return self.web3.eth.waitForTransactionReceipt(tx_hash)

    def hash_quote(self, quote):
        '''
        Generate the keccak hash of quote object.
        '''

        if quote.flag == Flag.off:
            self.k_value_or_nonce = quote.k_value
        if quote.flag == Flag.on:
            self.k_value_or_nonce = quote.k_value
        if quote.flag == Flag.na:
            self.k_value_or_nonce = quote.nonce

        return Web3.solidityKeccak(
            [
                "address",
                "address",
                "address",
                "address",
                "uint256",
                "uint256",
                "uint256",
                "uint256",
                "uint256",
                "bytes32"
            ],
            [self.web3.toChecksumAddress(quote.pool),
                self.web3.toChecksumAddress(quote.trader),
                self.web3.toChecksumAddress(quote.base_token_address),
                self.web3.toChecksumAddress(quote.quote_token_address),
                quote.base_token_amount,
                quote.quote_token_amount,
                quote.fees,
                self.k_value_or_nonce,
                quote.expiry,
                quote.txid
             ]
        ).hex()

    def hash_quote_eoa(self, quote):
        '''
        Generate the keccak hash of quote object.
        '''

        if quote.flag == Flag.off:
            self.k_value_or_nonce = quote.k_value
        if quote.flag == Flag.on:
            self.k_value_or_nonce = quote.k_value
        if quote.flag == Flag.na:
            self.k_value_or_nonce = quote.nonce

        return Web3.solidityKeccak(
            [
                "address",
                "address",
                "address",
                "address",
                "uint256",
                "uint256",
                "uint256",
                "uint256",
                "uint256",
                "bytes32"
            ],
            [self.web3.toChecksumAddress(quote.pool),
                self.web3.toChecksumAddress(quote.trader),
                self.web3.toChecksumAddress(quote.eoa),
                self.web3.toChecksumAddress(quote.base_token_address),
                self.web3.toChecksumAddress(quote.quote_token_address),
                quote.base_token_amount,
                quote.quote_token_amount,
                quote.fees,
                self.k_value_or_nonce,
                quote.expiry,
                quote.txid
             ]
        ).hex()

    def get_wallet_balance(
        self,
        account,
        token=None
    ):
        '''
        Gets the on-chain balance of a users wallet for some asset.
        '''
        if token is None:
            balance = self.web3.eth.getBalance(
                self.web3.toChecksumAddress(account))
        else:
            contract = self.create_contract(
                'IERC20',
                self.web3.toChecksumAddress(token)
            )
            balance = contract.functions.balanceOf(
                self.web3.toChecksumAddress(account)
            ).call()
        return balance

    def get_block_number(self):
        '''
        Gets the latest block number.
        '''
        return self.web3.eth.get_block_number()

    def set_expiry(self, expiry):
        '''
        Sets the quote expiry time (in seconds).
        '''
        result = int(time.time()) + expiry
        return result

    def convert_to_decimals(
        self,
        amount,
        token=None
    ):
        '''
        Convert asset amount to decimals.
        '''
        decimals = 18
        if token is not None:
            contract = self.create_contract(
                'IERC20',
                token,
            )
            decimals = contract.functions.decimals().call()

        return amount * (10**decimals)

    def convert_from_decimals(
        self,
        amount,
        token=None
    ):
        '''
        Convert asset amount from decimals.
        '''
        decimals = 18
        if token is not None:
            contract = self.create_contract(
                'IERC20',
                token,
            )
            decimals = contract.functions.decimals().call()

        return amount/(10**decimals)
