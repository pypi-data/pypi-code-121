import pytest
from web3.auto import w3

from .tools.test_openzeppelin import TestOpenzeppelin
from src.predeployed_generator.openzeppelin.proxy_admin_generator import ProxyAdminGenerator
from src.predeployed_generator.openzeppelin.transparent_upgradeable_proxy_generator import TransparentUpgradeableProxyGenerator
from src.predeployed_generator.upgradeable_contract_generator import UpgradeableContractGenerator

class TestTransparentUpgradeableProxyGenerator(TestOpenzeppelin):
    OWNER_ADDRESS = '0xd200000000000000000000000000000000000000'
    PROXY_ADMIN_ADDRESS = '0xd200000000000000000000000000000000000001'
    PROXY_ADDRESS = '0xD200000000000000000000000000000000000002'
    PROXY_ADDRESS_HASH = '0xf4CD0343eb019A7869A0D28c8C3A546a313fEB51'
    IMPLEMENTATION_ADDRESS = '0xd200000000000000000000000000000000000003'


    def get_transparent_upgradeable_proxy_abi(self) -> list:
        return self.get_abi('TransparentUpgradeableProxy')

    def get_proxy_admin_abi(self) -> list:
        return self.get_abi('ProxyAdmin')

    def prepare_genesis(self):
        proxy_admin_generator = ProxyAdminGenerator()
        upgradeable_contract_generator = UpgradeableContractGenerator(proxy_admin_generator)

        return self.generate_genesis({
            self.PROXY_ADMIN_ADDRESS: proxy_admin_generator.generate(owner_address=self.OWNER_ADDRESS),
            **upgradeable_contract_generator.generate_allocation(
                contract_address=self.PROXY_ADDRESS,
                implementation_address=self.IMPLEMENTATION_ADDRESS,
                proxy_admin_address=self.PROXY_ADMIN_ADDRESS,
                owner_address=self.OWNER_ADDRESS
            )
        })

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

    def test_default_implementation_address(self, tmpdir):
        self.datadir = tmpdir
        proxy_admin_generator = ProxyAdminGenerator()
        upgradeable_contract_generator = UpgradeableContractGenerator(proxy_admin_generator)

        genesis = self.generate_genesis({
            self.PROXY_ADMIN_ADDRESS: proxy_admin_generator.generate(owner_address=self.OWNER_ADDRESS),
            **upgradeable_contract_generator.generate_allocation(
                contract_address=self.PROXY_ADDRESS,
                proxy_admin_address=self.PROXY_ADMIN_ADDRESS,
                owner_address=self.OWNER_ADDRESS
            )
        })

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()
            
            proxy_admin = w3.eth.contract(address=self.PROXY_ADMIN_ADDRESS, abi=self.get_proxy_admin_abi())
            assert proxy_admin.functions.getProxyImplementation(self.PROXY_ADDRESS).call() == self.PROXY_ADDRESS_HASH
    
    def test_owner(self, tmpdir):
        self.datadir = tmpdir
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()
            
            proxy_admin = w3.eth.contract(address=self.PROXY_ADDRESS, abi=self.get_proxy_admin_abi())
            assert proxy_admin.functions.owner().call() == self.OWNER_ADDRESS

    def test_wrong_generation(self):
        with pytest.raises(RuntimeError):
            contract_generator = UpgradeableContractGenerator(ProxyAdminGenerator())
            contract_generator.generate()

    def test_balance_and_nonce(self, tmpdir):
        self.datadir = tmpdir
        proxy_admin_generator = ProxyAdminGenerator()
        upgradeable_contract_generator = UpgradeableContractGenerator(proxy_admin_generator)

        balance = 5
        nonce = 1

        genesis = self.generate_genesis({
            self.PROXY_ADMIN_ADDRESS: proxy_admin_generator.generate(owner_address=self.OWNER_ADDRESS),
            **upgradeable_contract_generator.generate_allocation(
                balance=balance,
                nonce=nonce,
                contract_address=self.PROXY_ADDRESS,
                implementation_address=self.IMPLEMENTATION_ADDRESS,
                proxy_admin_address=self.PROXY_ADMIN_ADDRESS,
                owner_address=self.OWNER_ADDRESS
            )
        })

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()
            
            assert w3.eth.get_balance(self.PROXY_ADDRESS) == balance
            assert w3.eth.get_transaction_count(self.PROXY_ADDRESS) == nonce

