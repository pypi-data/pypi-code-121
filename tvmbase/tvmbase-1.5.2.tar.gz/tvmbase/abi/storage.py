import json
import os

from loguru import logger
from tonclient.types import AbiContract

from tvmbase.abi.converter import json_to_abi
from tvmbase.utils.singleton import SingletonMeta


class AbiStorage(metaclass=SingletonMeta):

    def __init__(self, contracts_path: str, abi_path: str):
        self.contracts_path = contracts_path
        self.abi_path = abi_path
        self.abis, self.paths = self._load_abis()
        self._check_undetected_abis(self.paths)

    def _load_abis(self) -> (dict[str, AbiContract], set[str]):
        abis = dict()
        paths = set()
        contracts = self._load_json(self.contracts_path)
        for name, contract in contracts.items():
            abi_path = contract.get('abi_path')
            if abi_path is None:
                continue
            paths.add(abi_path)
            abi_full_path = os.path.join(self.abi_path, abi_path)
            abi_json = self._load_json(abi_full_path)
            abi = json_to_abi(abi_json)
            abis[name] = abi
        return abis, paths

    @staticmethod
    def _load_json(filename: str) -> dict:
        with open(filename) as file:
            return json.load(file)

    def _check_undetected_abis(self, found_paths: set[str]):
        all_paths = self.detected_abis_paths()
        undetected = all_paths - found_paths
        count = len(undetected)
        if count > 0:
            logger.warning(f'Found {count} undetected abis: {undetected}')

    def detected_abis_paths(self) -> set[str]:
        paths = set()
        for subdir, dirs, files in os.walk(self.abi_path, topdown=False):
            subdir = subdir.removeprefix(self.abi_path).lstrip('/')
            for file in files:
                if not file.endswith('.abi.json'):
                    continue
                path = os.path.join(subdir, file)
                paths.add(path)
        return paths

    def list(self) -> list[AbiContract]:
        return list(self.abis.values())

    def get(self, key: str, default: AbiContract = None) -> AbiContract:
        return self.abis.get(key, default)
