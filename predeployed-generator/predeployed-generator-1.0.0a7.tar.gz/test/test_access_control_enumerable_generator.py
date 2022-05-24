from web3.auto import w3

from .tools.custom_contract_generator import CustomContractGenerator
from .tools.test_solidity_project import TestSolidityProject


class TestAccessControlEnumerableGenerator(TestSolidityProject):
    OWNER_ADDRESS = '0xd200000000000000000000000000000000000000'
    TESTER_ADDRESS = '0xd200000000000000000000000000000000000001'
    TESTER2_ADDRESS = '0xD200000000000000000000000000000000000002'
    CONTRACT_ADDRESS = '0xd200000000000000000000000000000000000003'

    def get_test_contract_abi(self):
        return self.get_abi(CustomContractGenerator.CONTRACT_NAME)

    def prepare_genesis(self):
        test_contract_generator = CustomContractGenerator()

        return self.generate_genesis(test_contract_generator.generate_allocation(
            self.CONTRACT_ADDRESS,
            default_admin=self.OWNER_ADDRESS,
            testers=[self.TESTER_ADDRESS, self.TESTER2_ADDRESS]))
    
    def test_default_admin_role(self, tmpdir):
        self.datadir = tmpdir
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            test_contract = w3.eth.contract(address=self.CONTRACT_ADDRESS, abi=self.get_test_contract_abi())
            assert test_contract.functions.getRoleMemberCount(CustomContractGenerator.DEFAULT_ADMIN_ROLE).call() == 1
            assert test_contract.functions.getRoleMember(CustomContractGenerator.DEFAULT_ADMIN_ROLE, 0).call() == self.OWNER_ADDRESS            
            assert test_contract.functions.hasRole(CustomContractGenerator.DEFAULT_ADMIN_ROLE, self.OWNER_ADDRESS).call()

    def test_tester_role(self, tmpdir):
        self.datadir = tmpdir
        genesis = self.prepare_genesis()

        with self.run_geth(tmpdir, genesis):
            assert w3.isConnected()

            test_contract = w3.eth.contract(address=self.CONTRACT_ADDRESS, abi=self.get_test_contract_abi())
            assert test_contract.functions.getRoleMemberCount(CustomContractGenerator.TESTER_ROLE).call() == 2
            assert test_contract.functions.getRoleMember(CustomContractGenerator.TESTER_ROLE, 0).call() == self.TESTER_ADDRESS
            assert test_contract.functions.getRoleMember(CustomContractGenerator.TESTER_ROLE, 1).call() == self.TESTER2_ADDRESS
            assert test_contract.functions.hasRole(CustomContractGenerator.TESTER_ROLE, self.TESTER_ADDRESS).call()
            assert test_contract.functions.hasRole(CustomContractGenerator.TESTER_ROLE, self.TESTER2_ADDRESS).call()
