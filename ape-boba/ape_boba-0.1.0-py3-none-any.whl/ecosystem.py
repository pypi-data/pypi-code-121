from ape.api.config import PluginConfig
from ape.api.networks import LOCAL_NETWORK_NAME
from ape_ethereum.ecosystem import Ethereum, NetworkConfig

NETWORKS = {
    # chain_id, network_id
    "mainnet": (288, 288),
    "testnet": (28, 28),
}


class BobaConfig(PluginConfig):
    mainnet: NetworkConfig = NetworkConfig(required_confirmations=1, block_time=1)  # type: ignore
    testnet: NetworkConfig = NetworkConfig(required_confirmations=1, block_time=1)  # type: ignore
    local: NetworkConfig = NetworkConfig(default_provider="test")  # type: ignore
    default_network: str = LOCAL_NETWORK_NAME


class Boba(Ethereum):
    @property
    def config(self) -> BobaConfig:  # type: ignore
        return self.config_manager.get_config("boba")  # type: ignore
