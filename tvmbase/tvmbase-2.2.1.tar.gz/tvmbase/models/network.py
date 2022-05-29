from dataclasses import dataclass
from enum import Enum

from tonclient.client import MAINNET_BASE_URLS, DEVNET_BASE_URLS


@dataclass
class NetworkConfig:
    endpoints: list[str]
    everlive_domain: str
    everscan_domain: str


class Network(Enum):
    MAIN = NetworkConfig(
        MAINNET_BASE_URLS,
        'ever.live',
        'everscan.io',
    )
    DEV = NetworkConfig(
        DEVNET_BASE_URLS,
        'net.ever.live',
        'dev.tonscan.io',
    )
    RED = NetworkConfig(
        ['net.ton.red'],
        'net.ton.red',
        'everscan.io',
    )

    @classmethod
    def from_name(cls, name: str) -> 'Network':
        name = name.upper().removesuffix('NET')
        return cls[name]

    @property
    def value(self) -> NetworkConfig:
        return super().value
