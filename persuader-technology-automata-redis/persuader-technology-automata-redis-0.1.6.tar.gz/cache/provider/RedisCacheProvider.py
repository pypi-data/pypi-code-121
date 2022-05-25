import logging
from typing import TypeVar

import redis
from core.constants.not_available import NOT_AVAILABLE
from core.number.BigFloat import BigFloat
from core.options.exception.MissingOptionError import MissingOptionError
from coreutility.json.json_utility import as_pretty_json, as_json

T = TypeVar("T")

REDIS_SERVER_ADDRESS = 'REDIS_SERVER_ADDRESS'
REDIS_SERVER_PORT = 'REDIS_SERVER_PORT'


class RedisCacheProvider:

    def __init__(self, options, auto_connect=True):
        self.log = logging.getLogger('RedisCacheProvider')
        self.options = options
        self.auto_connect = auto_connect
        self.__check_options()
        if self.auto_connect:
            self.server_address = options[REDIS_SERVER_ADDRESS]
            self.server_port = options[REDIS_SERVER_PORT]
            self.log.info(f'Connecting to REDIS server {self.server_address}:{self.server_port}')
            self.redis_client = redis.Redis(host=self.server_address, port=self.server_port, decode_responses=True)
            self.redis_timeseries = self.redis_client.ts()

    def __check_options(self):
        if self.options is None:
            self.log.warning(f'missing option please provide options {REDIS_SERVER_ADDRESS} and {REDIS_SERVER_PORT}')
            raise MissingOptionError(f'missing option please provide options {REDIS_SERVER_ADDRESS} and {REDIS_SERVER_PORT}')
        if self.auto_connect is True:
            if REDIS_SERVER_ADDRESS not in self.options:
                self.log.warning(f'missing option please provide option {REDIS_SERVER_ADDRESS}')
                raise MissingOptionError(f'missing option please provide option {REDIS_SERVER_ADDRESS}')
            if REDIS_SERVER_PORT not in self.options:
                self.log.warning(f'missing option please provide option {REDIS_SERVER_PORT}')
                raise MissingOptionError(f'missing option please provide option {REDIS_SERVER_PORT}')

    def can_connect(self):
        try:
            return self.redis_client.ping()
        except redis.exceptions.ConnectionError:
            return False

    def get_keys(self, pattern='*'):
        return self.redis_client.keys(pattern)

    def store(self, key, value):
        if type(value) is BigFloat:
            self.redis_client.set(key, str(value))
        elif type(value) is list or type(value) is dict:
            serialized_json = as_pretty_json(value, indent=None)
            self.redis_client.set(key, serialized_json)
        else:
            self.redis_client.set(key, value)

    def fetch(self, key, as_type: T = str):
        value = self.redis_client.get(key)
        if value is not None and value == NOT_AVAILABLE:
            return NOT_AVAILABLE
        if as_type is int:
            return None if value is None else int(value)
        elif as_type is float:
            return None if value is None else float(value)
        elif as_type is BigFloat:
            return None if value is None else BigFloat(value)
        elif as_type is dict:
            result = as_json(value)
            return None if len(result) == 0 else result
        elif as_type is list:
            return as_json(value)
        else:
            return value

    def delete(self, key):
        self.redis_client.delete(key)

    @staticmethod
    def fraction_key(key):
        return f'{key}:fraction'

    @staticmethod
    def fraction_leading_zeros_key(key):
        return f'{key}:fraction:leading-zeros'

    def __create_timeseries(self, key, field_name, limit_retention):
        if not self.does_timeseries_exist(key):
            self.redis_timeseries.create(key, labels={'time': field_name}, retention_msecs=limit_retention)

    def create_timeseries(self, key, field_name, double_precision=False, limit_retention=0):
        self.__create_timeseries(key, field_name, limit_retention)
        if double_precision:
            self.__create_timeseries(self.fraction_key(key), field_name, limit_retention)
            self.__create_timeseries(self.fraction_leading_zeros_key(key), field_name, limit_retention)

    def add_to_timeseries(self, key, time, value):
        if type(value) is BigFloat:
            self.redis_timeseries.add(key, time, value.number)
            self.redis_timeseries.add(self.fraction_key(key), time, value.fraction)
            self.redis_timeseries.add(self.fraction_leading_zeros_key(key), time, value.fraction_leading_zeros)
        else:
            self.redis_timeseries.add(key, time, value)

    def get_timeseries_data(self, key, time_from, time_to, double_precision=False, reverse_direction=False):
        if double_precision:
            if reverse_direction is False:
                number_values = self.redis_timeseries.range(key, time_from, time_to)
                fraction_values = self.redis_timeseries.range(self.fraction_key(key), time_from, time_to)
                fraction_leading_zero_values = self.redis_timeseries.range(self.fraction_leading_zeros_key(key), time_from, time_to)
                return [(n1, BigFloat(int(v1), int(v2), int(v3))) for (n1, v1), (f2, v2), (l3, v3) in zip(number_values, fraction_values, fraction_leading_zero_values) if n1 == f2 and n1 == l3]
            else:
                number_values = self.redis_timeseries.revrange(key, time_from, time_to)
                fraction_values = self.redis_timeseries.revrange(self.fraction_key(key), time_from, time_to)
                fraction_leading_zero_values = self.redis_timeseries.revrange(self.fraction_leading_zeros_key(key), time_from, time_to)
                return [(n1, BigFloat(int(v1), int(v2), int(v3))) for (n1, v1), (f2, v2), (l3, v3) in zip(number_values, fraction_values, fraction_leading_zero_values) if n1 == f2 and n1 == l3]
        else:
            if reverse_direction is False:
                return self.redis_timeseries.range(key, time_from, time_to)
            else:
                return self.redis_timeseries.revrange(key, time_from, time_to)

    def does_timeseries_exist(self, timeseries_key):
        try:
            self.redis_timeseries.info(timeseries_key)
            return True
        except redis.exceptions.ResponseError:
            return False

    def delete_timeseries(self, key, double_precision=False):
        self.delete(key)
        if double_precision:
            self.delete(self.fraction_key(key))
            self.delete(self.fraction_leading_zeros_key(key))

    def get_timeseries_retention_time(self, timeseries_key):
        info = self.redis_timeseries.info(timeseries_key)
        return info.retention_msecs

