from dataclasses import dataclass

from tonclient.client import MAINNET_BASE_URLS, DEVNET_BASE_URLS


@dataclass(frozen=True, slots=True)
class Network:
    endpoints: list[str]
    ever_live_domain: str
    ever_scan_domain: str

    @classmethod
    def main(cls):
        return cls(
            MAINNET_BASE_URLS,
            'ever.live',
            'everscan.io',
        )

    @classmethod
    def dev(cls):
        return cls(
            DEVNET_BASE_URLS,
            'net.ever.live',
            'dev.tonscan.io',
        )

    @classmethod
    def red(cls):
        return (
            ['net.ton.red'],
            'net.ton.red',
            'everscan.io',
        )

    @classmethod
    def from_name(cls, name: str) -> 'Network':
        name = name.lower().removesuffix('net')
        return getattr(cls, name)()
