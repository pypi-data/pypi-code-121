
from multichain_explorer.src.providers.ada.ada_provider import AdaProvider
from multichain_explorer.src.providers.algo.algo_provider import AlgoProvider
from multichain_explorer.src.providers.btc.btc_provider import BtcProvider
from multichain_explorer.src.providers.eth.eth_provider import EthProvider
from multichain_explorer.src.providers.luna.luna_provider import LunaProvider
from multichain_explorer.src.providers.provider import ProviderInterface
from multichain_explorer.src.models.blockchains import Blockchains

class BlockchainProvider():

    def get_instance(blockchain_id: Blockchains) -> ProviderInterface:
        """
        Get the blockchain provider instance

        Args:
            blockchain_id: the blockchain id as an enum
        
        Returns:
            The blockchain provider instance wrapped in a ProviderInterface
        """
        match blockchain_id:
            case Blockchains.BTC:
                return BtcProvider()
            case Blockchains.ETH:
                return EthProvider()
            case Blockchains.ADA:
                return AdaProvider()
            case Blockchains.ALGO:
                return AlgoProvider()
            case Blockchains.LUNA:
                return LunaProvider()