from cache.holder.RedisCacheHolder import RedisCacheHolder
from core.options.exception.MissingOptionError import MissingOptionError
from core.position.Position import Position
from coreutility.string.string_utility import is_empty

from positionrepo.repository.serialize.position_deserializer import deserialize
from positionrepo.repository.serialize.position_serializer import serialize

POSITION_KEY = 'POSITION_KEY'
POSITION_HISTORY_LIMIT = 'POSITION_HISTORY_LIMIT'


class PositionRepository:

    def __init__(self, options):
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder()

    def __check_options(self):
        if self.options is None:
            raise MissingOptionError(f'missing option please provide options {POSITION_KEY}')
        if POSITION_KEY not in self.options:
            raise MissingOptionError(f'missing option please provide option {POSITION_KEY}')

    def __build_position_key(self):
        return self.options[POSITION_KEY]

    def __build_historic_positions_key(self):
        position_key = self.__build_position_key()
        return f'{position_key}:history'

    def store(self, position: Position):
        position_key = self.__build_position_key()
        position_serialized = serialize(position)
        self.cache.store(position_key, position_serialized)
        self.store_historical_position(position)

    def retrieve(self) -> Position:
        position_key = self.__build_position_key()
        raw_position = self.cache.fetch(position_key, as_type=dict)
        return deserialize(raw_position)

    def store_historical_position(self, position: Position):
        if is_empty(position.exchanged_from) is False:
            historical_positions = self.retrieve_historic_positions()
            if self.__is_already_history(position, historical_positions) is False:
                historical_positions.append(position)
                self.__store_historical_positions_with_limit(historical_positions)

    @staticmethod
    def __is_already_history(position, historical_positions):
        matching_positions = list([hp for hp in historical_positions if hp == position])
        return len(matching_positions) > 0

    def __store_historical_positions_with_limit(self, historical_positions):
        entities_to_store = list([serialize(p) for p in historical_positions])
        if POSITION_HISTORY_LIMIT in self.options:
            if len(entities_to_store) > int(self.options[POSITION_HISTORY_LIMIT]):
                entities_to_store = entities_to_store[1:]
        key = self.__build_historic_positions_key()
        self.cache.store(key, entities_to_store)

    def retrieve_historic_positions(self):
        key = self.__build_historic_positions_key()
        raw_entities = self.cache.fetch(key, as_type=list)
        return list([deserialize(raw) for raw in raw_entities])
