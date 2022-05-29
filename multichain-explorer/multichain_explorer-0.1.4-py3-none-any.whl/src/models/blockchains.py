from enum import Enum

class Blockchains(Enum):
    ETH = "ETH"
    BTC = "BTC"
    ADA = "ADA"
    ALGO = "ALGO"
    LUNA = "LUNA"

    def get_available_blockchains():
        """
        Get all the blockchain id's

        Returns:
            The blockchains ids as a list
        """
        available_blockchains = [] 
        for blockchain in Blockchains:
            available_blockchains.append(blockchain)
        return available_blockchains