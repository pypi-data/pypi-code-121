from cryptos import *
from multichain_explorer.src.models.blockchains import Blockchains
from multichain_explorer.src.services.coinmarketcap_service import CoinMarketCapService
from multichain_explorer.src.validators.btc.btc_validator import BtcValidator
from multichain_explorer.src.validators.validator import ValidatorInterface
from multichain_explorer.src.models.provider_options import ProviderOptions
from multichain_explorer.src.providers.provider import ProviderInterface


class BtcProvider(ProviderInterface):
    
    validator: ValidatorInterface
    coinMarketCapService : CoinMarketCapService


    def __init__(self):
        self.provider = Bitcoin()
        self.validator = BtcValidator()
        self.coinMarketCapService : CoinMarketCapService()


    def get_summary(self):
        data = CoinMarketCapService().fetchData(Blockchains.BTC.value)
        cryptoData = data['data'][Blockchains.BTC.value]
        currency = "USD"

        summary = {
            "name" : cryptoData['name'],
            "price" : cryptoData['quote'][currency]['price'],
            "marketCap" : cryptoData['quote'][currency]['market_cap'],
            "totalSupply" : cryptoData['total_supply']
        }
        return summary


    def get_blocks(self, num_blocks = 10, options = ProviderOptions()):
        """ Returns a list of BTC block data, default number of blocks is 10 """

        latest_block_number = self.provider.current_block_height()
        latest_blocks = []

        for block_number in range(latest_block_number, 
                                latest_block_number - num_blocks, 
                                -1):
            block_data = self.get_block_by_id(block_number)
            latest_blocks.append(block_data)

        return latest_blocks


    def get_block_by_id(self, block_id = 'latest', options = ProviderOptions()):
        #If id is a number cast to int
        try:
            if block_id == 'latest':
                block_id = self.provider.current_block_height()
            else:
                block_id = int(block_id) #Cast to int
                
            block = self.provider.block_info(block_id)
            block_data = {
                "id" : block_id,
                "miner" : "-",
                "difficulty" : str( self.count_leading_zeroes(block['hash']) ) + " (target)",
                "timestamp": block['timestamp'],
            }

            if options.raw:
                #TODO - Pass real raw block data in the rawData field 
                #block_data["rawData"] = block
                block_data["rawData"] = {}

        except ValueError as err:
            # Log exception
            raise

        return block_data


    def count_leading_zeroes(text : str):
       #Count leading zeroes in a string
        match = re.match(r'^0+', text)
        return 0 if match is None else len(match.group())


    def get_transactions(self, num_tx = 10, options = ProviderOptions()):
        """Returns a list of transactions, default number of transactions is 10"""
        try:
            block_height = self.provider.current_block_height()
            #Get latest transactions
            block_transactions = self.provider.block_info(block_height)['tx_hashes']

            latest_transactions = []

            # Get the last num_tx transactions from block (default is 10)
            for transaction_id in block_transactions[-num_tx:]:
                #Convert id from binary hex to string
                transaction_data = self.get_transaction_by_id(transaction_id)
                latest_transactions.append(transaction_data)

        except ValueError as err:
            # Log exception
            raise
        return latest_transactions


    def get_transaction_by_id(self, tx_id = 'latest', options = ProviderOptions()):
        """Get an Algorand transaction by id"""

        if tx_id == 'latest':
            block_height = self.provider.current_block_height()
            #Get latest transaction id
            tx_id = self.provider.block_info(block_height)['tx_hashes'][-1]
        
        tx = self.provider.fetchtx(tx_id)

        transaction_data = {
            "id"         : tx_id,
            "from"       : tx['inputs'][0]['prev_out']['addr'],
            "to"         : tx['out'][0]['addr'],
            "value"      : tx['out'][0]['value'],  # value in satoshis
            "block"      : tx['block_index']
        }

        return transaction_data


    def get_address(self, address_id):
        """Get the info of an Algorand account"""

        try:
            history = self.provider.history(address_id)
            balance = history['final_balance'] # balance in satoshis

            return {
                "address" : address_id,
                "balance" : balance
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