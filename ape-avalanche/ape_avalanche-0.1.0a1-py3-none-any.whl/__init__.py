from ape import plugins
from ape.api import NetworkAPI, create_network_type
from ape.api.networks import LOCAL_NETWORK_NAME
from ape_geth import GethProvider
from ape_test import LocalProvider

from .ecosystem import NETWORKS, Avalanche, AvalancheConfig


@plugins.register(plugins.Config)
def config_class():
    return AvalancheConfig


@plugins.register(plugins.EcosystemPlugin)
def ecosystems():
    yield Avalanche


@plugins.register(plugins.NetworkPlugin)
def networks():
    for network_name, network_params in NETWORKS.items():
        yield "avalanche", network_name, create_network_type(*network_params)

    # NOTE: This works for development providers, as they get chain_id from themselves
    yield "avalanche", LOCAL_NETWORK_NAME, NetworkAPI
    yield "avalanche", "mainnet-fork", NetworkAPI


@plugins.register(plugins.ProviderPlugin)
def providers():
    for network_name in NETWORKS:
        yield "avalanche", network_name, GethProvider

    yield "avalanche", LOCAL_NETWORK_NAME, LocalProvider
