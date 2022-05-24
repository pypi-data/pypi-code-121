from web3.auto import w3

from .tools.test_openzeppelin import TestOpenzeppelin
from src.predeployed_generator.openzeppelin.proxy_admin_generator import ProxyAdminGenerator
from src.predeployed_generator.openzeppelin.transparent_upgradeable_proxy_generator import TransparentUpgradeableProxyGenerator

class TestTransparentUpgradeableProxyGenerator(TestOpenzeppelin):
    OWNER_ADDRESS = '0xd200000000000000000000000000000000000000'
    PROXY_ADMIN_ADDRESS = '0xd200000000000000000000000000000000000001'
    PROXY_ADDRESS = '0xD200000000000000000000000000000000000002'
    IMPLEMENTATION_ADDRESS = '0xd200000000000000000000000000000000000003'


    def get_transparent_upgradeable_proxy_abi(self) -> list:
        return self.get_abi('TransparentUpgradeableProxy')


    def get_proxy_admin_abi(self) -> list:
        return self.get_abi('ProxyAdmin')

    def prepare_genesis(self):
        proxy_admin_generator = ProxyAdminGenerator()
        proxy_generator = TransparentUpgradeableProxyGenerator()

        genesis = self.generate_genesis({
            self.PROXY_ADMIN_ADDRESS: proxy_admin_generator.generate(owner_address=self.OWNER_ADDRESS),
            self.PROXY_ADDRESS: proxy_generator.generate(
                implementation_address=self.IMPLEMENTATION_ADDRESS,
                admin_address=self.PROXY_ADMIN_ADDRESS,
                initial_storage=proxy_admin_generator.generate_storage(owner_address=self.OWNER_ADDRESS)
            ),
            self.IMPLEMENTATION_ADDRESS: proxy_admin_generator.generate(owner_address=self.OWNER_ADDRESS)
        })
        return genesis

    # tests

    def test_admin(self, tmpdir):   
        self.datadir = tmpdir     
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()
            
            proxy_admin = w3.eth.contract(address=self.PROXY_ADMIN_ADDRESS, abi=self.get_proxy_admin_abi())
            assert proxy_admin.functions.getProxyAdmin(self.PROXY_ADDRESS).call() == self.PROXY_ADMIN_ADDRESS

    def test_implementation(self, tmpdir):
        self.datadir = tmpdir
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()
            
            proxy_admin = w3.eth.contract(address=self.PROXY_ADMIN_ADDRESS, abi=self.get_proxy_admin_abi())
            assert proxy_admin.functions.getProxyImplementation(self.PROXY_ADDRESS).call() == self.IMPLEMENTATION_ADDRESS 

