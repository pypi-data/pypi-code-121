import logging
from typing import List

from cache.holder.RedisCacheHolder import RedisCacheHolder
from core.options.exception.MissingOptionError import MissingOptionError

from processrepo.Process import Process
from processrepo.repository.serialize.process_deserializer import deserialize_process
from processrepo.repository.serialize.process_serializer import serialize_process

PROCESS_KEY = 'PROCESS_KEY'


class ProcessRepository:

    def __init__(self, options):
        self.log = logging.getLogger(__name__)
        self.options = options
        self.__check_options()
        self.process_key = self.options[PROCESS_KEY]
        self.cache = RedisCacheHolder()

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {PROCESS_KEY}')
            raise MissingOptionError(f'missing option please provide options {PROCESS_KEY}')
        if PROCESS_KEY not in self.options:
            self.log.warning(f'missing option please provide option {PROCESS_KEY}')
            raise MissingOptionError(f'missing option please provide option {PROCESS_KEY}')

    def build_process_key(self, market, process_name):
        return self.process_key.format(market, process_name)

    def store(self, process: Process):
        key = self.build_process_key(process.market, process.name)
        serialized = serialize_process(process)
        self.cache.store(key, serialized)

    def retrieve(self, process_name, market) -> Process:
        key = self.build_process_key(market, process_name)
        return self.__retrieve(key)

    def __retrieve(self, key):
        raw_entity = self.cache.fetch(key, as_type=dict)
        return deserialize_process(raw_entity)

    def retrieve_all(self, market) -> List[Process]:
        all_process_keys = self.process_key.format(market, '*')
        keys = self.cache.get_keys(all_process_keys)
        return list([self.__retrieve(pk) for pk in keys])
