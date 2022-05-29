
from multichain_explorer.src.models.blockchains import Blockchains
from multichain_explorer.src.services.coinmarketcap_service import CoinMarketCapService
from multichain_explorer.src.validators.algo.algo_validator import AlgoValidator
from multichain_explorer.src.validators.validator import ValidatorInterface
from multichain_explorer.src.models.provider_options import ProviderOptions
from multichain_explorer.src.providers.provider import ProviderInterface

from algosdk.v2client import algod
from algosdk.v2client import indexer


class AlgoProvider(ProviderInterface):

    # To load from config file
    ALGOD_TOKEN : str     = ""
    ALGOD_ADDRESS : str   = ""
    INDEXER_ADDRESS : str = ""

    validator: ValidatorInterface = AlgoValidator()
    coinMarketCapService : CoinMarketCapService = CoinMarketCapService()


    def __init__(self):
        headers = { "X-API-Key": self.ALGOD_TOKEN }
        self.provider = algod.AlgodClient(self.ALGOD_TOKEN, self.ALGOD_ADDRESS, headers)
        self.provider.indexer = indexer.IndexerClient(self.ALGOD_TOKEN, self.INDEXER_ADDRESS, headers)


    def get_summary(self):
        data = CoinMarketCapService().fetchData(Blockchains.ALGO.value)
        cryptoData = data['data'][Blockchains.ALGO.value]
        currency = "USD"

        summary = {
            "name" : cryptoData['name'],
            "price" : cryptoData['quote'][currency]['price'],
            "marketCap" : cryptoData['quote'][currency]['market_cap'],
            "totalSupply" : cryptoData['total_supply']
        }
        return summary


    def get_blocks(self, num_blocks = 10, options = ProviderOptions()):
        latest_block_number = self.provider.status()['last-round']
        latest_blocks = []

        for block_number in range(latest_block_number, 
                                latest_block_number - num_blocks, 
                                -1):
            block_data = self.get_block_by_id(block_number)
            latest_blocks.append(block_data)
        
        return latest_blocks


    def get_block_by_id(self, block_id = 'latest', options = ProviderOptions()):
        try:
            if block_id == 'latest':
                status = self.provider.status()
                last_round = status.get("last-round")
                block = self.provider.block_info(last_round)
            else:
                block_id = int(block_id) #Cast to int
                block = self.provider.block_info(block_id)

            block_data = {
                "id" : block['block']['rnd'],
                "miner" : "-",
                "difficulty" : "-",
                "timestamp": block['block']['ts']
            }

            if options.raw:
                    block_data["rawData"] = {}

            return block_data
        except Exception as e:
            print(e)


    def get_transactions(self, num_tx = 10, options = ProviderOptions()):
        """Returns a list of transactions, default number of transactions is 10"""
        try:
            last_round = self.provider.status()['last-round']
            #Get latest transactions
            block_transactions = self.provider.indexer.search_transactions(block=last_round)['transactions']
            latest_transactions = []

            # Get the last num_tx transactions from block (default is 10)
            for transaction in block_transactions[-num_tx:]:
                #Convert id from binary hex to string
                transaction_data = self.get_transaction_by_id(transaction['id'])
                latest_transactions.append(transaction_data)

        except ValueError as err:
            # Log exception
            raise
        return latest_transactions


    def get_transaction_by_id(self, tx_id = 'latest', options = ProviderOptions()):
        """Get an Algorand transaction by id"""

        if tx_id == 'latest':
            last_round = self.provider.status()['last-round']
            #Get latest transaction id
            tx_id = self.provider.indexer.search_transactions(block=last_round)['transactions'][-1]['id']
        
        transaction = self.provider.indexer.transaction(tx_id)

        #Get receiver based on transaction type
        receiver = '-'
        value = 0
        tx_type = transaction['transaction']['tx-type']

        if tx_type == 'pay':
            tx_type_details = transaction['transaction']['payment-transaction']
            receiver = tx_type_details['receiver']
            value = tx_type_details['amount']
        elif tx_type == 'axfer':
            tx_type_details = transaction['transaction']['asset-transfer-transaction']
            receiver = tx_type_details['receiver']
            value = tx_type_details['amount']

        transaction_data = {
            "id"         : transaction['transaction']['id'],
            "from"       : transaction['transaction']['sender'],
            "to"         : receiver,
            "value"      : value, 
            "block"      : transaction['transaction']['confirmed-round'],
        }

        return transaction_data


    def get_address(self, address_id):
        """Get the info of an Algorand account"""
        try:
            account_info = self.provider.account_info(address_id)
            return {
                "address" : address_id,
                "balance" : account_info.get("amount")
            }
        except Exception as err:
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