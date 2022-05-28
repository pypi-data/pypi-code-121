from ape.api.config import PluginConfig
from ape.api.networks import LOCAL_NETWORK_NAME
from ape_ethereum.ecosystem import Ethereum, NetworkConfig

NETWORKS = {
    # chain_id, network_id
    "mainnet": (43114, 43114),
    "fuji": (43113, 43113),
}


class AvalancheConfig(PluginConfig):
    mainnet: NetworkConfig = NetworkConfig(required_confirmations=1, block_time=2)  # type: ignore
    fuji: NetworkConfig = NetworkConfig(required_confirmations=1, block_time=2)  # type: ignore
    local: NetworkConfig = NetworkConfig(default_provider="test")  # type: ignore
    default_network: str = LOCAL_NETWORK_NAME


class Avalanche(Ethereum):
    @property
    def config(self) -> AvalancheConfig:  # type: ignore
        return self.config_manager.get_config("avalanche")  # type: ignore
