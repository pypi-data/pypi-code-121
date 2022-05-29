from multichain_explorer.src.validators.validator import ValidatorInterface
import re

class EthValidator(ValidatorInterface):

    blockRegex = r"^[0-9]{1,20}$"
    addressRegex = r"^0x[a-fA-F0-9]{40}$"
    transactionRegex = r"^0x[a-f0-9]{64}$"


    def is_block(self, text: str) -> bool:
        """Checks whether the text matches an ETH block number signature"""
        return bool( re.match(self.blockRegex, text) )

    def is_address(self, text: str) -> bool:
        """Checks whether the text matches an ETH address signature"""
        return bool( re.match(self.addressRegex, text) )

    def is_transaction(self, text: str) -> bool:
        """Checks whether the text matches an ETH block transaction signature"""        
        return bool( re.match(self.transactionRegex, text) )
