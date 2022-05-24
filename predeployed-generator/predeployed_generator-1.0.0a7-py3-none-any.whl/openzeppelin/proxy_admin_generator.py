'''proxy_admin_generator.py

Module for generation of proxy admin

classes:
    ProxyAdminGenerator
'''

from typing import Dict

from .openzeppelin_contract_generator import OpenzeppelinContractGenerator


class ProxyAdminGenerator(OpenzeppelinContractGenerator):
    '''Generates ProxyAdmin
    '''

    ARTIFACT_FILENAME = 'ProxyAdmin.json'

    OWNER_SLOT = 0

    # ---------- storage ----------
    # -----------Context-----------
    # -----------Ownable-----------
    # 0:    _owner
    # ---------ProxyAdmin----------

    @staticmethod
    def generate_storage(**kwargs) -> Dict[str, str]:
        owner_address = kwargs['owner_address']
        storage: Dict[str, str] = {}
        ProxyAdminGenerator._write_address(
            storage,
            ProxyAdminGenerator.OWNER_SLOT,
            owner_address)
        return storage
