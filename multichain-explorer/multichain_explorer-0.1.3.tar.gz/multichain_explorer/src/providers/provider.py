import abc
from typing import List
from multichain_explorer.src.models.provider_options import ProviderOptions
from multichain_explorer.src.models.provider_models import Address, Block

class ProviderInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_summary') and 
                callable(subclass.get_summary) and 
                hasattr(subclass, 'get_blocks') and 
                callable(subclass.get_blocks) and 
                hasattr(subclass, 'get_block_by_id') and 
                callable(subclass.get_block_by_id) and
                hasattr(subclass, 'get_transactions') and 
                callable(subclass.get_transactions) and 
                hasattr(subclass, 'get_transaction_by_id') and 
                callable(subclass.get_transaction_by_id) and 
                callable(subclass.get_address) and 
                hasattr(subclass, 'get_address') and 
                callable(subclass.search_resource) and 
                hasattr(subclass, 'search_resource') or 
                NotImplemented)

    @abc.abstractmethod
    def get_summary(self):
        """
        Get a summary of the blockchain

        Returns:
            A dict containing the summary data of the blockchain
            The dict has the following structure:
            {
                "name" : blockchain_name,
                "price" : token_price,
                "marketCap" : market_cap,
                "totalSupply" : total_supply
            }
                
        Raises:
            NotImplementedError if the method is not implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_blocks(self, num_blocks: int, options: ProviderOptions):
        """ Get a list of blocks
        
        Args:
            num_blocks: number of blocks to return
            options: ProviderOptions object 

        Returns:
            The list of blocks
            
        Raises:
            NotImplementedError if the method is not implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_block_by_id(self, block_id: str, options: ProviderOptions):
        """ Get a block by id
        
        Args:
            block_id: id of the block
            options: ProviderOptions object 

        Returns:
            A dict containing the block data
            The dict has the following structure:
            {
                "id"            : block_number,
                "miner"         : miner,
                "difficulty"    : difficulty,
                "timestamp"     : timestamp,
                "rawData"       : raw_data (optional)
            }
            
        Raises:
            NotImplementedError if the method is not implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_transactions(self, num_tx: int, options: ProviderOptions):
        """Get a list of transactions
        
        Args:
            num_tx: number of transactions to return
            options: ProviderOptions object
        
        Returns:
            A list of transactions

        Raises:
            NotImplementedError if the method is not implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_transaction_by_id(self, tx_id: str, options: ProviderOptions):
        """Get a transaction by id
        
        Args:
            tx_id: id of the transaction

        Returns:
            A dict containing the transaction data
            The dict has the following structure:
            {
                "id"    : tx_id,
                "from"  : transaction_from,
                "to"    : transaction_to,
                "value" : transaction_value,
                "block" : transaction_blockNumber
                "rawData" : transaction_rawData (optional)
            } 
        
        Raises:
            NotImplementedError if the method is not implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_address(self, address_id):
        """Returns an address by its address identifier
        
        Args:
            address_id: address identifier

        Returns:
            A dict containing the address data
            The dict has the following structure:
            {
                "id"        : address_id,
                "balance"   : address_balance,
            }
        
        Raises:
            NotImplementedError if the method is not implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    def search_resource(self, search_text):
        """Search for a resource (block, address or transaction) by search_text
        
        Args:
            search_text: the text to search for
        
        Returns:
            A dict containing the resource (block, address or transaction) data
            The dict has the following structure:
            {
                "type"  : type ("block", "address" or "transaction"),
                "data"  : dict with block, address or transaction data
            }
        
        Raises:
            NotImplementedError if the method is not implemented
        """
        raise NotImplementedError