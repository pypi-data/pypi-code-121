'''transparent_upgradeable_proxy_generator.py

Module for generation of transparent upgradeable proxy

classes:
    TransparentUpgradeableProxyGenerator
'''

from typing import Dict

from web3.auto import w3

from .openzeppelin_contract_generator import OpenzeppelinContractGenerator


class TransparentUpgradeableProxyGenerator(OpenzeppelinContractGenerator):
    '''Generates transparent upgradeable proxy
    '''
    ARTIFACT_FILENAME = 'TransparentUpgradeableProxy.json'
    ROLLBACK_SLOT = int.from_bytes(
        w3.solidityKeccak(['string'], ['eip1967.proxy.rollback']),
        byteorder='big') - 1
    IMPLEMENTATION_SLOT = int.from_bytes(
        w3.solidityKeccak(['string'], ['eip1967.proxy.implementation']),
        byteorder='big') - 1
    ADMIN_SLOT = int.from_bytes(
        w3.solidityKeccak(['string'], ['eip1967.proxy.admin']),
        byteorder='big') - 1

    @staticmethod
    def generate_storage(**kwargs) -> dict:
        '''Generate contract storage

        Arguments:
            - implementation_address
            - admin_address

        Optional arguments:
            - initial_storage
        '''
        implementation_address = kwargs['implementation_address']
        admin_address = kwargs['admin_address']
        initial_storage = kwargs.get('initial_storage', None)
        storage: Dict[str, str] = {}
        TransparentUpgradeableProxyGenerator._write_address(
            storage,
            TransparentUpgradeableProxyGenerator.IMPLEMENTATION_SLOT,
            implementation_address)
        TransparentUpgradeableProxyGenerator._write_address(
            storage,
            TransparentUpgradeableProxyGenerator.ADMIN_SLOT,
            admin_address)
        if initial_storage is not None:
            storage.update(initial_storage)
        return storage
