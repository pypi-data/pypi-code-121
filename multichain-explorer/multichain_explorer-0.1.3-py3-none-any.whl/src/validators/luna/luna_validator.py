from multichain_explorer.src.validators.validator import ValidatorInterface
import re

class LunaValidator(ValidatorInterface):

    blockRegex = r"^$"
    addressRegex = r"^$"
    transactionRegex = r"^$"


    def is_block(self, text: str) -> bool:
        """Checks whether the text matches an LUNA block number signature"""
        return bool( re.match(self.blockRegex, text) )

    def is_address(self, text: str) -> bool:
        """Checks whether the text matches an LUNA address signature"""
        return bool( re.match(self.addressRegex, text) )

    def is_transaction(self, text: str) -> bool:
        """Checks whether the text matches an LUNA block transaction signature"""        
        return bool( re.match(self.transactionRegex, text) )
