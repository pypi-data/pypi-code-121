import resource
from typing import Optional, Union

from bitmath import MiB
from hbutils.model import get_repr_info
from hbutils.scale import size_to_bytes, time_to_duration, size_to_bytes_str

from ...utils import allow_none

_UNLIMITED = -1


def _rmin(x, y):
    if x == _UNLIMITED:
        return y
    elif y == _UNLIMITED:
        return x
    else:
        return min(x, y)


def _rprocess(cur, new):
    _cur_soft, _cur_hard = cur
    if isinstance(new, tuple):
        _new_soft, _new_hard = new
    else:
        _new_soft, _new_hard = new, new

    _hard = _rmin(_cur_hard, _new_hard)
    _soft = _rmin(_new_soft, _hard)

    return _soft, _hard


_memory_process = allow_none(size_to_bytes)
_duration_process = allow_none(time_to_duration)
_number_process = allow_none(lambda x: x)


class ResourceLimit:
    __RESOURCES = {"max_stack", "max_memory", "max_cpu_time", "max_real_time",
                   "max_process_number", "max_output_size", }

    def __init__(
            self,
            max_stack=None,
            max_memory=None,
            max_cpu_time=None,
            max_real_time=None,
            max_process_number=None,
            max_output_size=None
    ):
        """
        :param max_stack: max stack memory (unit: B)
        :param max_memory: max rss memory memory (unit: B)
        :param max_cpu_time: max cpu time (unit: s)
        :param max_real_time: max real time (unit: s)
        :param max_process_number: max process count
        :param max_output_size: max output size (unit: B)
        """
        self.__max_stack = _memory_process(max_stack)
        self.__max_memory = _memory_process(max_memory)
        self.__max_cpu_time = _duration_process(max_cpu_time)
        self.__max_real_time = _duration_process(max_real_time)
        self.__max_process_number = _number_process(max_process_number)
        self.__max_output_size = _memory_process(max_output_size)

    @property
    def max_stack(self):
        """
        :return: max stack size (size: B)
        """
        return self.__max_stack

    @property
    def max_memory(self):
        """
        :return: max rss memory size (size: B)
        """
        return self.__max_memory

    @property
    def max_cpu_time(self):
        """
        :return: max cpu time (unit: s)
        """
        return self.__max_cpu_time

    @property
    def max_real_time(self):
        """
        :return: max real time (unit: s)
        """
        return self.__max_real_time

    @property
    def max_process_number(self):
        """
        :return: max process count
        """
        return self.__max_process_number

    @property
    def max_output_size(self):
        """
        :return: max output size (unit: B)
        """
        return self.__max_output_size

    @classmethod
    def __apply_limit(cls, limit_type, value):
        """
        apply one of the resources
        :param limit_type: type of limitation
        :param value: limitation value
        """
        _limit_value = _rprocess(resource.getrlimit(limit_type), value)
        resource.setrlimit(limit_type, _limit_value)

    def __apply_max_stack(self):
        """
        apply max stack limit
        """
        if self.max_stack:
            real = self.max_stack
        else:
            real = _UNLIMITED
        self.__apply_limit(resource.RLIMIT_STACK, real)

    def __apply_max_memory(self):
        """
        apply max rss memory limit
        """
        if self.max_memory:
            real = round(self.max_memory + MiB(256).bytes)
        else:
            real = _UNLIMITED
        self.__apply_limit(resource.RLIMIT_AS, real)

    def __apply_max_cpu_time(self):
        """
        apply max cpu time limit
        """
        if self.max_cpu_time:
            real = round(self.max_cpu_time) + 1
        else:
            real = _UNLIMITED
        self.__apply_limit(resource.RLIMIT_CPU, real)

    def __apply_max_process_number(self):
        """
        apply max process number limit
        """
        if self.max_process_number:
            real = self.max_process_number
        else:
            real = _UNLIMITED
        self.__apply_limit(resource.RLIMIT_NPROC, real)

    def __apply_max_output_size(self):
        """
        apply max output size limit
        """
        if self.max_output_size:
            real = self.max_output_size
        else:
            real = _UNLIMITED
        self.__apply_limit(resource.RLIMIT_FSIZE, real)

    @property
    def json(self):
        """
        get json format data
        :return: json format data
        """
        return {
            "max_memory": self.max_memory,
            "max_stack": self.max_stack,
            "max_process_number": self.max_process_number,
            "max_output_size": self.max_output_size,
            "max_cpu_time": self.max_cpu_time,
            "max_real_time": self.max_real_time,
        }

    @classmethod
    def load_from_json(cls, json_data: dict) -> 'ResourceLimit':
        """
        load object from json data
        :param json_data: json data
        :return: resource limit object
        """
        return cls(**cls.__filter_by_properties(**json_data))

    @classmethod
    def loads(cls, data: Optional[Union[dict, 'ResourceLimit']]) -> 'ResourceLimit':
        """
        load object from json data or resource limit object
        :param data: json data or object
        :return: resource limit object
        """
        data = data or {}
        if isinstance(data, ResourceLimit):
            return data
        elif isinstance(data, dict):
            return ResourceLimit.load_from_json(json_data=data)
        else:
            raise TypeError('{rl} or {dict} expected, but {actual} found.'.format(
                rl=ResourceLimit.__name__,
                dict=dict.__name__,
                actual=type(data).__name__,
            ))

    def apply(self):
        """
        apply the resource limits
        """
        self.__apply_max_process_number()
        self.__apply_max_stack()
        self.__apply_max_memory()
        self.__apply_max_output_size()
        self.__apply_max_cpu_time()

    @classmethod
    def __filter_by_properties(cls, **kwargs):
        """
        filter the arguments by properties
        :param kwargs: original arguments
        :return: filtered arguments
        """
        return {
            key: value for key, value in kwargs.items() if key in cls.__RESOURCES
        }

    @classmethod
    def merge(cls, *limits: 'ResourceLimit'):
        """
        merge some of the limits
        :param limits: list of the limits
        :return: merged limits
        """

        def _get_min_limitation(array, property_method):
            _values = [_item for _item in [property_method(_item) for _item in array if _item] if _item is not None]
            if _values:
                return min(_values)
            else:
                return None

        _max_stack = _get_min_limitation(limits, lambda _item: _item.max_stack)
        _max_memory = _get_min_limitation(limits, lambda _item: _item.max_memory)
        _max_cpu_time = _get_min_limitation(limits, lambda _item: _item.max_cpu_time)
        _max_real_time = _get_min_limitation(limits, lambda _item: _item.max_real_time)
        _max_process_number = _get_min_limitation(limits, lambda _item: _item.max_process_number)
        _max_output_size = _get_min_limitation(limits, lambda _item: _item.max_output_size)

        return cls(
            max_stack=_max_stack,
            max_memory=_max_memory,
            max_cpu_time=_max_cpu_time,
            max_real_time=_max_real_time,
            max_process_number=_max_process_number,
            max_output_size=_max_output_size,
        )

    def __tuple(self):
        return self.__max_stack, self.__max_memory, self.__max_cpu_time, \
               self.__max_real_time, self.__max_process_number, self.__max_output_size

    def __eq__(self, other):
        if other is self:
            return True
        elif isinstance(other, self.__class__):
            return self.__tuple() == other.__tuple()
        else:
            return False

    def __hash__(self):
        return hash(self.__tuple())

    def __repr__(self):
        return get_repr_info(
            cls=self.__class__,
            args=[
                ('cpu time', (lambda: '%.3fs' % self.max_cpu_time, lambda: self.max_cpu_time is not None)),
                ('real time', (lambda: '%.3fs' % self.max_real_time, lambda: self.max_real_time is not None)),
                ('memory', (lambda: size_to_bytes_str(self.max_memory), lambda: self.max_memory is not None)),
                ('stack', (lambda: size_to_bytes_str(self.max_stack), lambda: self.max_stack is not None)),
                ('process', (lambda: self.max_process_number, lambda: self.max_process_number is not None)),
                ('output size',
                 (lambda: size_to_bytes_str(self.max_output_size), lambda: self.max_output_size is not None)),
            ]
        )
