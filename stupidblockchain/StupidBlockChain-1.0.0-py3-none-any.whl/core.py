import json
import time
import typing
from dataclasses import asdict, dataclass

from . import utils


@dataclass
class Header:
    nonce: int
    hash: bytes


@dataclass
class Payload:
    sequence: int
    data: str
    timestamp: int
    prev_hash: bytes


@dataclass
class Block:
    header: Header
    payload: Payload

    @property
    def hash(self):
        return self.header.hash

    @property
    def prev_hash(self):
        return self.payload.prev_hash

    @property
    def sequence(self):
        return self.payload.sequence

    @property
    def nonce(self):
        return self.header.nonce

    @property
    def data(self):
        return json.loads(self.payload.data)

    def __repr__(self) -> str:
        return f"Block<{utils.hexdigest(self.hash)[:10]}...>"


class InvalidBlockException(Exception):
    def __init__(self, invalid_block: Block, message=None):
        self.block = invalid_block
        super().__init__(message)


class BlockChain:
    def __init__(self, difficulty: int = 4, proof_of_work_preffix: str = '0'):
        self._chain: list[Block] = []

        self._difficulty = difficulty
        self._preffix = proof_of_work_preffix

        self._create_genesis_block()

    @staticmethod
    def _to_json(data: dict[str, str]):
        return json.dumps(data, ensure_ascii=False).encode('utf8')

    def _create_genesis_block(self):
        block_payload = Payload(sequence=0, data='Where it all started', timestamp=time.time_ns(), prev_hash='')
        block_header = Header(hash=utils.digest(self._to_json(asdict(block_payload))), nonce=0)

        self._chain.append(Block(block_header, block_payload))

    @property
    def _last_block(self) -> Block:
        return self._chain[-1]

    @property
    def size(self) -> int:
        return self._last_block.sequence + 1

    def create_block(self, data: typing.Any) -> Block:
        block_payload = Payload(
            sequence=self.size,
            data=json.dumps(data),
            timestamp=time.time_ns(),
            prev_hash=self._last_block.hash)

        return Block(Header(0, b'0'*256), block_payload)

    def mine(self, block: Block) -> float:
        nonce: int = 0
        start_time = time.time()

        while True:
            payload_dict = asdict(block.payload)
            payload_dict['prev_hash'] = utils.hexdigest(payload_dict['prev_hash'])
            payload_dict['nonce'] = nonce

            hash = utils.digest(self._to_json(payload_dict))

            if not utils.is_hash_proofed(hash, self._difficulty, self._preffix):
                nonce += 1

                continue

            mine_time = time.time() - start_time

            print(f"Took {mine_time:5.5} seconds to mine block #{block.sequence}!")

            header = Header(nonce, hash)
            block.header = header

            return mine_time

    def _is_new_block_valid(self, block: Block) -> bool:
        if block.prev_hash != self._last_block.hash:
            raise InvalidBlockException(
                block,
                f"Block #{block.sequence} invalid! Previous hash is {self._last_block.hash[:10]!r}, "
                f"but got {block.hash[:10]!r}.")

        elif not utils.is_hash_proofed(block.hash, self._difficulty, self._preffix):
            raise InvalidBlockException(block, f"Block #{block.sequence} invalid! Its signature is invalid. "
                                               f"Got nonce {block.nonce}")

        return True

    def add_block(self, block: Block):
        if self._is_new_block_valid(block):
            self._chain.append(block)

            print(f"Successfully added {block}!")
