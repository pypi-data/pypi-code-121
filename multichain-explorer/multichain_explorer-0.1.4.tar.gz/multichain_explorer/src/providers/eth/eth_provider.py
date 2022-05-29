from web3   import Web3
from multichain_explorer.src.models.blockchains import Blockchains
from multichain_explorer.src.services.coinmarketcap_service import CoinMarketCapService
from multichain_explorer.src.validators.eth.eth_validator import EthValidator
from multichain_explorer.src.validators.validator import ValidatorInterface
from multichain_explorer.src.models.provider_options import ProviderOptions
from multichain_explorer.src.providers.provider import ProviderInterface


class EthProvider(ProviderInterface):
    
    # Must be set externally by the caller
    INFURA_URL : str = ""
    validator : ValidatorInterface = EthValidator()
    coinMarketCapService : CoinMarketCapService = CoinMarketCapService()


    def __init__(self):
        self.provider = Web3(Web3.HTTPProvider(self.INFURA_URL))


    def get_summary(self):
        data = CoinMarketCapService().fetchData(Blockchains.ETH.value)
        cryptoData = data['data'][Blockchains.ETH.value]
        currency = "USD"

        summary = {
            "name" : cryptoData['name'],
            "price" : cryptoData['quote'][currency]['price'],
            "marketCap" : cryptoData['quote'][currency]['market_cap'],
            "totalSupply" : cryptoData['total_supply']
        }
        return summary


    def get_blocks(self, num_blocks = 10, options = ProviderOptions()):
        latest_blocks = []
        # Would be nice if calls were asynchronous
        for block_number in range(self.provider.eth.block_number, 
                                  self.provider.eth.block_number-num_blocks, 
                                  -1):
            block_data = self.get_block_by_id(block_number, options)
            latest_blocks.append(block_data)
        return latest_blocks


    def get_block_by_id(self, block_id = 'latest', options = ProviderOptions()):
        #If id is a number cast to int
        if type(block_id) == str and block_id.isnumeric():
            block_id = int(block_id)
        
        try:
            block = self.provider.eth.get_block(block_id)
            block_data = {
                "id" : block.number,
                "miner" : block.miner,
                "difficulty" : block.difficulty,
                "timestamp": block.timestamp,
            }

            if options.raw:
                block_data["rawData"] = self.provider.toJSON(block)

        except ValueError as err:
            # Log exception
            raise

        return block_data


    def get_transactions(self, num_tx = 10, options = ProviderOptions()):
        """Returns a list of transactions, default number of transactions is 10"""
        try:
            block = self.provider.eth.get_block("latest")
            block_transactions = block.transactions
            latest_transactions = []

            # Get the last num_tx transactions from block (default is 10)
            for transaction_id in block_transactions[-num_tx:]:
                #Convert id from binary hex to string
                transaction_data = self.get_transaction_by_id(transaction_id.hex(), options)
                latest_transactions.append(transaction_data)

        except ValueError as err:
            # Log exception
            raise
        return latest_transactions


    def get_transaction_by_id(self, tx_id = 'latest', options = ProviderOptions()):
        """Get an Ethereum transaction by id"""
        transaction = self.provider.eth.get_transaction(tx_id)
        transaction_data = {
            "id"    : tx_id,
            "from"  : transaction['from'],
            "to"    : transaction['to'],
            "value" : transaction['value'],
            "block" : transaction['blockNumber']
        }

        if options.raw:
            transaction_data["rawData"] = self.provider.toJSON(transaction)

        return transaction_data


    def get_address(self, address_id):
        try:
            balance = self.provider.eth.get_balance(address_id)
            balance = self.provider.fromWei(balance, 'ether')
            return {
                "address"   : address_id,
                "balance"   : balance
            }
        except Exception as err:
            #log error
            raise

    
    def search_resource(self, search_text):
        if self.validator.is_block(search_text):
            block = self.get_block_by_id(search_text)
            return { "type" : "block", "data" : block }
        if self.validator.is_address(search_text):
            address = self.get_address(search_text)
            return { "type" : "address", "data" : address }
        if self.validator.is_transaction(search_text):
            transaction = self.get_transaction_by_id(search_text)
            return { "type" : "transaction", "data" : transaction }
            
        raise