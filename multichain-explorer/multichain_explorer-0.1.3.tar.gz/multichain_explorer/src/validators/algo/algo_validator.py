from multichain_explorer.src.validators.validator import ValidatorInterface
import re

class AlgoValidator(ValidatorInterface):

    blockRegex = r"^$"
    addressRegex = r"^$"
    transactionRegex = r"^$"


    def is_block(self, text: str) -> bool:
        """Checks whether the text matches an ALGO block number signature"""
        return bool( re.match(self.blockRegex, text) )

    def is_address(self, text: str) -> bool:
        """Checks whether the text matches an ALGO address signature"""
        return bool( re.match(self.addressRegex, text) )

    def is_transaction(self, text: str) -> bool:
        """Checks whether the text matches an ALGO block transaction signature"""        
        return bool( re.match(self.transactionRegex, text) )
