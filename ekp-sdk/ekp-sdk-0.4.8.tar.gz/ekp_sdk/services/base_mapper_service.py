from ast import literal_eval

from ekp_sdk.domain.log import Log
from ekp_sdk.dto.etherscan_log_dto import EtherscanLogDto
from ekp_sdk.dto.web3_log_dto import Web3LogDto


class BaseMapperService:

    def map_hex_to_int(self, hex: str):
        if hex is None:
            return None

        if isinstance(hex, int):
            return hex

        if not isinstance(hex, str):
            return None

        if hex.startswith("0x"):
            return literal_eval(hex)

        return int(hex, 16)

    def map_etherscan_log_dto_to_domain(self, dto: EtherscanLogDto) -> Log:
        log: Log = {
            'address': dto['address'],
            'block_number': self.map_hex_to_int(dto['blockNumber']),
            'data': dto['data'],
            'gas_price': self.map_hex_to_int(dto['gasPrice']),
            'gas_used': self.map_hex_to_int(dto['gasUsed']),
            'log_index': self.map_hex_to_int(dto['logIndex']),
            'timestamp': self.map_hex_to_int(dto['timeStamp']),
            'topics': dto['topics'],
            'transaction_hash': dto['transactionHash'],
            'transaction_index': self.map_hex_to_int(dto['transactionIndex']),
        }

        return log

    def map_web3_log_dto_to_domain(self, dto: Web3LogDto) -> Log:
        log: Log = {
            'address': dto['address'],
            'block_number': dto['blockNumber'],
            'data': dto['data'],
            'log_index': dto['logIndex'],
            'topics': dto['topics'],
            'transaction_hash': dto['transactionHash'],
            'transaction_index': dto['transactionIndex'],
        }

        return log
