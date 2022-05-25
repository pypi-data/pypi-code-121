from cache.holder.RedisCacheHolder import RedisCacheHolder
from core.options.exception.MissingOptionError import MissingOptionError
from core.position.PositionSlip import PositionSlip

from positionrepo.repository.serialize.position_slip_deserializer import deserialize
from positionrepo.repository.serialize.position_slip_serializer import serialize

POSITION_SLIP_KEY = 'POSITION_SLIP_KEY'


class PositionSlipRepository:

    def __init__(self, options):
        self.options = options
        self.__check_options()
        self.cache = RedisCacheHolder()

    def __check_options(self):
        if self.options is None:
            raise MissingOptionError(f'missing option please provide options {POSITION_SLIP_KEY}')
        if POSITION_SLIP_KEY not in self.options:
            raise MissingOptionError(f'missing option please provide option {POSITION_SLIP_KEY}')

    def store(self, position_slip: PositionSlip):
        position_slip_key = self.options[POSITION_SLIP_KEY]
        slip_serialized = serialize(position_slip)
        self.cache.store(position_slip_key, slip_serialized)

    def retrieve(self) -> PositionSlip:
        position_slip_key = self.options[POSITION_SLIP_KEY]
        raw_slip = self.cache.fetch(position_slip_key, as_type=dict)
        return deserialize(raw_slip)

