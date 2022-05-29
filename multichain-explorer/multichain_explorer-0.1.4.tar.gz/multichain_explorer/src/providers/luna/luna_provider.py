
from multichain_explorer.src.models.blockchains import Blockchains
from multichain_explorer.src.services.coinmarketcap_service import CoinMarketCapService
from multichain_explorer.src.validators.luna.luna_validator import LunaValidator
from multichain_explorer.src.validators.validator import ValidatorInterface
from multichain_explorer.src.models.provider_options import ProviderOptions
from multichain_explorer.src.providers.provider import ProviderInterface

from typing import List
from terra_sdk.client.lcd import LCDClient

class LunaProvider(ProviderInterface):
    
    # Must be set externally by the caller
    TERRA_CHAIN_ID  : str = ""
    TERRA_URL       : str = ""

    validator: ValidatorInterface = LunaValidator()
    coinMarketCapService : CoinMarketCapService = CoinMarketCapService()


    def __init__(self):
        self.provider = LCDClient(chain_id = self.TERRA_CHAIN_ID, url = self.TERRA_URL)


    def get_summary(self):
        data = CoinMarketCapService().fetchData(Blockchains.LUNA.value)
        cryptoData = data['data'][Blockchains.LUNA.value]
        currency = "USD"

        summary = {
            "name" : cryptoData['name'],
            "price" : cryptoData['quote'][currency]['price'],
            "marketCap" : cryptoData['quote'][currency]['market_cap'],
            "totalSupply" : cryptoData['total_supply']
        }
        return summary


    def get_blocks(self, num_blocks = 10, options = ProviderOptions()):
        latest_block_number = int( self.provider.tendermint.block_info()['block']['header']['height'] )
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
                block = self.provider.tendermint.block_info()
            else:
                block_id = int(block_id) #Cast to int
                block = self.provider.tendermint.block_info(block_id)

            block_data = {
                "id" :block_id,
                "miner" : block['block']['header']['proposer_address'],
                "difficulty" : "-",
                "timestamp": block['block']['header']['time']
            }
            
            if options.raw:
                block_data["rawData"] = {}

            return block_data

        except Exception as e:
            raise


    def get_transactions(self, num_tx = 10, options = ProviderOptions()):
        """Returns a list of transactions, default number of transactions is 10"""
        try:
            block_transactions = self.provider.tx.tx_infos_by_height()
            latest_transactions = []

            # Get the last num_tx transactions from block (default is 10)
            for transaction in block_transactions[-num_tx:]:
                transaction_data = self.extractTxData(transaction, options)
                latest_transactions.append(transaction_data)

        except ValueError as err:
            # Log exception
            raise
        
        return latest_transactions


    def get_transaction_by_id(self, tx_id = 'latest', options = ProviderOptions()):
        """Get a Terra transaction by id"""
        if tx_id == 'latest':
            tx_id = self.provider.tx.tx_infos_by_height()[-1].txhash

        try:
            tx = self.provider.tx.tx_info(tx_id)
            transaction_data = self.extractTxData(tx, options)
            return transaction_data
        except Exception as err:
            raise


    def get_address(self, address_id):
        try:
            address = self.provider.bank.balance(address_id)
            address_info = {
                "address"   : address_id,
                "balance"   : self._print_balance(address[0].to_data())
            }

            return address_info
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


    def extractTxData(self, tx, options = ProviderOptions()) -> dict:
        """Extracts data from a transaction"""
        
        # Get the transaction data based on transaction type
        from_address = ""
        to_address = ""  
        value = ""

        if type( tx.tx.body.messages[0] ).__name__ == 'MsgSend':
            from_address = tx.tx.body.messages[0].from_address
            to_address = tx.tx.body.messages[0].to_address
            value = self._print_coins( tx.tx.body.messages[0].amount.to_data() )
        elif type( tx.tx.body.messages[0] ).__name__ == 'MsgExecuteContract':
            from_address = tx.tx.body.messages[0].sender
            to_address = tx.tx.body.messages[0].contract  
            value = self._print_coins( tx.tx.body.messages[0].coins.to_data() )
        elif type( tx.tx.body.messages[0] ).__name__ == 'MsgMultiSend':
            from_address = ""
            to_address = ""  
            value = ""
        elif type( tx.tx.body.messages[0] ).__name__ == 'MsgWithdrawDelegationReward':
            from_address = ""
            to_address = ""  
            value = ""
        elif type( tx.tx.body.messages[0] ).__name__ == 'MsgWithdrawValidatorCommission':
            from_address = ""
            to_address = ""  
            value = ""
        elif type( tx.tx.body.messages[0] ).__name__ == 'MsgAggregateExchangeRateVote':
            from_address = ""
            to_address = ""  
            value = ""

        tx_data = {
                "id"    : tx.txhash,
                "from"  : from_address,
                "to"    : to_address,
                "value" : value,
                "block" : tx.height
            }
        
        if options.raw:
            #TODO - Add raw data
            tx_data["rawData"] = {}

        return tx_data


    def _print_coins(self, coins: List[dict]) -> str:
        """Returns a string with the formatted coins ('denom: amount')
        
        Args:
            coins (List[dict]): List of coins

        returns:
            str: Formatted coins
        """

        if len(coins) == 0:
            return "0"
        else:
            format_coins = lambda coin: f"{coin['amount']} ({coin['denom']})"
            formatted_coins = map(format_coins, coins)
            return ", ".join(formatted_coins)


    def _print_balance(self, balances: List[dict]) -> str:
        """Returns a string with the formatted balances ('denom: amount')
        
        Args:
            balances (List[dict]): List of balances

        returns:
            str: Formatted balances
        """

        if len(balances) == 0:
            return "0"
        else:
            format_balance = lambda balance: f"{balance['amount']} ({balance['denom']})"
            formatted_balances = map(format_balance, balances)
            return ", ".join(formatted_balances)


