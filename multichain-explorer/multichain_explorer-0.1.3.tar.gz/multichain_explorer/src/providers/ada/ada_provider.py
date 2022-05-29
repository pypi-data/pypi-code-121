
from multichain_explorer.src.models.blockchains import Blockchains
from multichain_explorer.src.services.coinmarketcap_service import CoinMarketCapService
from multichain_explorer.src.validators.ada.ada_validator import AdaValidator
from multichain_explorer.src.validators.validator import ValidatorInterface
from multichain_explorer.src.models.provider_options import ProviderOptions
from multichain_explorer.src.providers.provider import ProviderInterface
from blockfrost import BlockFrostApi, ApiError

class AdaProvider(ProviderInterface):
    
    validator: ValidatorInterface
    coinMarketCapService : CoinMarketCapService


    def __init__(self):
        self.provider = BlockFrostApi(project_id='mainnetugnPOWiXzieqDhohU5S1UWUsyvaXHLCz')
        self.validator = AdaValidator()
        self.coinMarketCapService : CoinMarketCapService()


    def get_summary(self):
        data = CoinMarketCapService().fetchData(Blockchains.ADA.value)
        cryptoData = data['data'][Blockchains.ADA.value]
        currency = "USD"

        summary = {
            "name" : cryptoData['name'],
            "price" : cryptoData['quote'][currency]['price'],
            "marketCap" : cryptoData['quote'][currency]['market_cap'],
            "totalSupply" : cryptoData['total_supply']
        }
        return summary


    def get_blocks(self, num_blocks = 10, options = ProviderOptions()):
        latest_block_number = self.get_block_by_id('latest').height
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
                block = self.provider.block_latest()
            else:
                block = self.provider.block(block_id)

            block_data = {
                "id" : block.height,
                "miner" : block.slot_leader,
                "difficulty" : "-",
                "timestamp" : block.time,
                "block_hash" : block.hash
            }

            if options.raw:
                    block_data["rawData"] = {}
            
            return block_data
        except ApiError as e:
            print(e)

        return block_data


    def get_transactions(self, num_tx = 10, options = ProviderOptions()):
        """Returns a list of transactions, default number of transactions is 10"""
        try:
            block_transactions = self.provider.block_latest_transactions()
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
        """Get a Cardano transaction by id"""

        if tx_id == 'latest':
            tx_id = self.provider.block_latest_transactions()[0]
        
        transaction = self.provider.transaction(tx_id)
        tx_utxos = self.provider.transaction_utxos(tx_id)

        transaction_data = {
            "id"    : transaction.hash, #tx_id,
            "from"  : tx_utxos.inputs[0].address, 
            "to"    : tx_utxos.outputs[0].address,
            "value" : tx_utxos.outputs[0].amount[0].quantity, 
            "block" : transaction.block_height,
            "block_hash" : transaction.block
        }

        return transaction_data


    def get_address(self, address_id):
        try:
            address_info = self.provider.address(address_id)
            return {
                "address"   : address_id,
                "balance"   : address_info.amount[0].quantity
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