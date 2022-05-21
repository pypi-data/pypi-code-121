from passql.exceptions import SqlException
from typing_extensions import TypeAlias
from typing import Dict, Type, Any, Callable, Optional
import re

__all__ = (
    'Sql',
    'SqlMaker',
    'SqlConverter',
)

ValueToSqlConverter: TypeAlias = Callable[[Any, 'SqlConverter'], str]


class Sql:
    __slots__ = ('_converter', '_strings', '_params')

    __PRM_PATTERN = re.compile(r"@[\w]+")

    def __init__(self, converter: 'SqlConverter', string: str):
        self._converter = converter
        self._strings = []
        self._params = []

        string = string.strip()
        last = 0
        for m in re.finditer(Sql.__PRM_PATTERN, string):
            start = m.start(0)

            if start - 2 > 0:
                if string[start - 1] == '\\':
                    if string[start - 2] != '\\':
                        continue
            elif start - 1 > 0:
                if string[start - 1] == '\\':
                    continue

            s = string[last:start]
            if s:
                self._strings.append(s)

            last = m.end(0)
            self._params.append(string[start + 1:last])

        s = string[last:]
        if s or not self._strings:
            self._strings.append(s)

        if not self._params:
            self._params = None

    def __repr__(self):
        if self._strings:
            short_preview = self._strings[0][:10] + \
                            ('..., ' if len(self._strings) > 1 or len(self._strings[0]) > 10 else ', ')
        else:
            short_preview = ''
        params = f"{len(self._params)} param" + ('' if self._params == 1 else 's')
        return f"<Sql: {short_preview}{params}>"

    def __str__(self):
        if self._params is not None:
            raise SqlException(f"Cannot convert {self.__class__.__name__} to string, parameters required!")

        return self._strings[0]

    def format(self, obj: Optional) -> str:
        """
        Parse parameters from obj to sql template.

        :param obj: Any object or dictionary with required fields/keys.
        """
        if self._params is None:
            return self._strings[0]

        result = []
        prm_length = len(self._params)

        if type(obj) is dict:
            for i in range(len(self._strings)):
                result.append(self._strings[i])
                if i < prm_length:
                    value = obj[self._params[i]]
                    result.append(value.format(obj) if type(value) is Sql else self._converter(value))
        else:
            for i in range(len(self._strings)):
                result.append(self._strings[i])
                if i < prm_length:
                    value = getattr(obj, self._params[i])
                    result.append(value.format(obj) if type(value) is Sql else self._converter(value))

        return ''.join(result)


class SqlMaker:
    __slots__ = ('_converter', )

    # noinspection PyTypeChecker
    __EMPTY = Sql(None, "")

    def __init__(self, converter: 'SqlConverter'):
        self._converter = converter

    def __call__(self, string: str) -> Sql:
        return Sql(self._converter, string)

    @classmethod
    def empty(cls) -> 'Sql':
        return cls.__EMPTY


class SqlConverter:
    __slots__ = ('_type_to_converter', )

    def __init__(self, type_to_converter_map: Dict[Type, ValueToSqlConverter]):
        self._type_to_converter = {}
        for t in type_to_converter_map:
            self._type_to_converter[t] = type_to_converter_map[t]

    def __call__(self, value: Any) -> str:
        converter = self._type_to_converter.get(type(value))
        if converter is None:
            raise SqlException(f"Type of mapping object '{value}' has no any convertor!")

        return converter(value, self)

    def __add__(self, other: 'SqlConverter') -> 'SqlConverter':
        type_to_converters = {}

        for t, converter in self._type_to_converter.items():
            type_to_converters[t] = converter
        for t, converter in other._type_to_converter.items():
            type_to_converters[t] = converter

        return SqlConverter(type_to_converters)
