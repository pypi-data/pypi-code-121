'''upgradeable_contract_generator.py

The module is used to generate predeployed smart contracts in genesis block
that is upgradeable using EIP-1967 tranparent upgradeable proxy

Classes:
    UpgradeableContractGenerator
'''

from web3.auto import w3

from .openzeppelin.transparent_upgradeable_proxy_generator \
    import TransparentUpgradeableProxyGenerator
from .contract_generator import ContractGenerator


class UpgradeableContractGenerator(TransparentUpgradeableProxyGenerator):
    '''Generates transparent upgradeable proxy based on implementation generator'''
    def __init__(
            self,
            implementation_generator: ContractGenerator):
        super().__init__()
        self.implementation_generator = implementation_generator

    def generate(self, balance=0, nonce=0, **_) -> ContractGenerator.Account:
        raise RuntimeError('''Can\'t generate upgradeable contract without implementation.
Use `generate_allocation` method instead''')

    def generate_allocation(
        self, contract_address, balance=0, nonce=0, **kwargs
    ) -> ContractGenerator.Allocation:
        '''Generate smart contract allocation.
        It's pair of 2 smart contract:
        the first is upgradeable proxy
        and the second is an implementation

        If `implementation_address` parameter is not specified
        address of implementation is first 20 bytes of keccak256(`contract_address`)

        Arguments:
            - proxy_admin_address
            - arguments required by implementation contract generator

        Optional arguments:
            - implementation_address
            - balance
            - nonce

        Returns an object in format:
        {
            "0xd2...": {
                'balance': ... ,
                'nonce': ... ,
                'code': ... ,
                'storage': ...
            },
            "0xd2...": {
                'balance': ... ,
                'nonce': ... ,
                'code': ... ,
                'storage': ...
            }
        }
        '''
        proxy_admin_address = kwargs.pop('proxy_admin_address')
        implementation_address = kwargs.pop(
            'implementation_address',
            w3.toChecksumAddress(w3.solidityKeccak(['address'], [contract_address])[:20]))

        return {
            contract_address: super().generate(
                admin_address=proxy_admin_address,
                implementation_address=implementation_address,
                initial_storage=self.implementation_generator.generate_storage(**kwargs),
                balance=balance,
                nonce=nonce),
            # pylint: disable=W0212
            implementation_address: self.implementation_generator._generate(storage=None)}
