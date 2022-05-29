import abc

class ValidatorInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'is_block') and 
                callable(subclass.is_block) and 
                hasattr(subclass, 'is_address') and 
                callable(subclass.is_address) or
                hasattr(subclass, 'is_transaction') and 
                callable(subclass.is_transaction) and  
                NotImplemented)

    @abc.abstractmethod
    def is_block(self, text: str) -> bool:
        """Checks whether the text matches a block number signature
        
        Args:
            text: text to check against the block number signature
        
        Returns:
            True if the text matches the block number signature, False otherwise
        """
        raise NotImplementedError

    @abc.abstractmethod
    def is_address(self, text: str) -> bool:
        """Checks whether the text matches an address signature
        
        Args:
            text: text to validate against address regex

        Returns:
            True if the text matches the address regex, False otherwise
        """
        raise NotImplementedError

    @abc.abstractmethod
    def is_transaction(self, text: str) -> bool:
        """Checks whether the text matches a transaction signature
        
        Args:
            text: text to validate against transaction regex

        Returns:
            True if the text matches the transaction regex, False otherwise
        """
        raise NotImplementedError