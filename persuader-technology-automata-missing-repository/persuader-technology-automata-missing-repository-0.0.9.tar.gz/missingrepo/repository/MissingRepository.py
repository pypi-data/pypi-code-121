import logging
from typing import List

from cache.holder.RedisCacheHolder import RedisCacheHolder
from core.options.exception.MissingOptionError import MissingOptionError

from missingrepo.Missing import Missing
from missingrepo.repository.serialize.missing_deserializer import deserialize_missing
from missingrepo.repository.serialize.missing_serializer import serialize_missing

MISSING_KEY = 'MISSING_KEY'


class MissingRepository:

    def __init__(self, options):
        self.log = logging.getLogger(__name__)
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder()

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {MISSING_KEY}')
            raise MissingOptionError(f'missing option please provide options {MISSING_KEY}')
        if MISSING_KEY not in self.options:
            self.log.warning(f'missing option please provide option {MISSING_KEY}')
            raise MissingOptionError(f'missing option please provide option {MISSING_KEY}')

    def store(self, missing):
        if type(missing) is Missing:
            self.__store_append(missing)
        elif type(missing) is list:
            self.__store_all(missing)

    def retrieve(self) -> List[Missing]:
        key = self.options[MISSING_KEY]
        raw_entities = self.cache.fetch(key, as_type=list)
        entities = list([deserialize_missing(raw) for raw in raw_entities])
        return entities

    def __store_append(self, missing: Missing):
        all_missing = self.retrieve()
        if missing not in all_missing:
            all_missing.append(missing)
            self.store(all_missing)

    def __store_all(self, multiple_missing):
        if len(multiple_missing) > 0:
            key = self.options[MISSING_KEY]
            entities_to_store = list([serialize_missing(missing) for missing in multiple_missing])
            self.log.debug(f'Storing {len(entities_to_store)} missing')
            self.cache.store(key, entities_to_store)

    def is_already_missing(self, missing):
        all_missing = self.retrieve()
        return missing in all_missing
