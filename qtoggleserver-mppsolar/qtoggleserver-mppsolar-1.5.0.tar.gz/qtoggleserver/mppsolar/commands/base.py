
import ctypes
import re

from typing import Optional, Tuple

from ..exceptions import MPPSolarException
from ..typing import Properties, PropertyDefinitions


SUFFIXES = ('__choices',)


class CommandException(MPPSolarException):
    pass


class ResponseError(CommandException):
    pass


class Command:
    REQUEST_FMT = ''
    RESPONSE_FMT = ''
    VIRTUAL_PROPERTIES = {}
    UNITS = {}
    DISPLAY_NAMES = {}
    CHOICES = {}
    REQUEST_DEFAULT_VALUES = {}

    _TYPE_MAP = {
        'int': int,
        'float': float,
        'bool': bool,
        'str': str
    }

    _response_regex: Optional[Tuple[Optional[re.Pattern], re.Pattern]] = None
    _request_property_definitions: Optional[PropertyDefinitions] = None
    _response_property_definitions: Optional[PropertyDefinitions] = None

    def __init__(self, **params) -> None:
        self._params = params

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__.split('_')[0]

    def prepare_request(self) -> bytes:
        message = self.REQUEST_FMT.format(**self._params)
        return message.encode() + self.compute_crc(message) + b'\r'

    def parse_response(self, response: bytes) -> Properties:
        if not response.startswith(b'('):
            raise ResponseError(f'Unexpected response start: {response}')

        if not response.endswith(b'\r'):
            raise ResponseError(f'Unexpected response end: {response}')

        response = response[:-1]  # Get rid of terminal '\r'

        crc = response[-2:]
        response = response[:-2].decode()
        if self.compute_crc(response) != crc:
            raise ResponseError(f'Wrong CRC: {response} {repr(crc)[2:-1]}')

        response = response[1:]  # Get rid of start byte '('

        split_pat, values_pat = self.get_response_regex()
        if split_pat:
            parts = split_pat.split(response)
        else:
            parts = [response]

        parsed_dict = {}
        for part in parts:
            match = values_pat.match(part)
            if not match:
                raise ResponseError(f'Unexpected response format: {response}')

            for name, value in match.groupdict().items():
                type_, name = name.split('_', 1)
                parsed_value = self._TYPE_MAP[type_](value)
                if split_pat:
                    parsed_dict.setdefault(name, []).append(parsed_value)
                else:
                    parsed_dict[name] = parsed_value

        # Add virtual properties
        for name, details in self.VIRTUAL_PROPERTIES.items():
            if not details:
                continue  # property disabled in command subclass
            if name in parsed_dict:
                continue  # property already present

            parsed_dict[name] = details['value'](parsed_dict)

        return parsed_dict

    @classmethod
    def get_request_property_definitions(cls) -> PropertyDefinitions:
        if cls._request_property_definitions is None:
            matches = re.findall(r'{([^:]+):([.0-9dfbs]+)}', cls.REQUEST_FMT)
            cls._request_property_definitions = {
                name: {
                    'format': format_
                } for name, format_ in matches if not name.startswith('_')
            }

        return cls._request_property_definitions

    @classmethod
    def get_response_property_definitions(cls) -> PropertyDefinitions:
        if cls._response_property_definitions is None:
            is_list = False
            response_fmt = cls.RESPONSE_FMT
            if response_fmt.endswith('...'):
                is_list = True
                response_fmt = response_fmt[:-3]

            matches = re.findall(r'{([^:]+):([dfbs])}', response_fmt)
            matches += [(name, details['type']) for name, details in cls.VIRTUAL_PROPERTIES.items() if details]
            type_mapping = {
                'd': 'int',
                'f': 'float',
                'b': 'bool',
                's': 'str'
            }
            cls._response_property_definitions = {
                re.sub('|'.join(SUFFIXES), '', name): {
                    'type': type_mapping.get(type_, type_),
                    'is_list': is_list,
                    'is_choices': name.endswith('__choices'),
                    'unit': cls.UNITS.get(name),
                    'display_name': cls.DISPLAY_NAMES.get(name),
                    'choices': [
                        {'value': choice[0], 'display_name': choice[1]}
                        for choice in cls.CHOICES[name]
                    ] if name in cls.CHOICES else None
                } for name, type_ in matches if not name.startswith('_')
            }

        return cls._response_property_definitions

    @classmethod
    def has_response_properties(cls) -> bool:
        for details in cls.get_response_property_definitions().values():
            if not details['is_choices']:
                return True

        return False

    @classmethod
    def get_response_regex(cls) -> Tuple[Optional[re.Pattern], re.Pattern]:
        if cls._response_regex is None:
            pat = cls.RESPONSE_FMT
            is_list = False
            if pat.endswith('...'):
                pat = pat[:-3]
                is_list = True
            pat = re.sub('|'.join(SUFFIXES), '', pat)
            pat = re.sub(r'\s+', '\\\\s+', pat)
            pat = re.sub(r'{([^:]+):d}', '(?P<int_\\1>-?[0-9]+)', pat)
            pat = re.sub(r'{([^:]+):f}', '(?P<float_\\1>-?[0-9.]+)', pat)
            pat = re.sub(r'{([^:]+):b}', '(?P<bool_\\1>[01])', pat)
            pat = re.sub(r'{([^:]+):s}', '(?P<str_\\1>[^\\\\s]+)', pat)
            cls._response_regex = (re.compile(r'\s+') if is_list else None, re.compile(pat))

        return cls._response_regex

    @staticmethod
    def compute_crc(message: str) -> bytes:
        crc = 0
        crc_ta = [
            0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
            0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef
        ]

        for c in message:
            c = ord(c)

            t_da = ctypes.c_uint8(crc >> 8)
            da = t_da.value >> 4
            crc <<= 4
            index = da ^ (c >> 4)
            crc ^= crc_ta[index]
            t_da = ctypes.c_uint8(crc >> 8)
            da = t_da.value >> 4
            crc <<= 4
            index = da ^ (c & 0x0f)
            crc ^= crc_ta[index]

        crc_low = ctypes.c_uint8(crc).value
        crc_high = ctypes.c_uint8(crc >> 8).value

        if crc_low in (0x28, 0x0d, 0x0a):
            crc_low += 1

        if crc_high in (0x28, 0x0d, 0x0a):
            crc_high += 1

        return bytes((crc_high, crc_low))
