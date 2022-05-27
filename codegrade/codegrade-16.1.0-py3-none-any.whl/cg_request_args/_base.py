"""
The base classes for ``cg_request_args``.

This file contains the base parser class, and simple classes that you can use
to parse primitive types.
"""
import abc
import copy
import typing as t

import structlog

import cg_maybe

from ._utils import T_COV as _T_COV
from ._utils import USE_SLOTS as _USE_SLOTS
from ._utils import T as _T
from ._utils import Y as _Y
from ._utils import Final, type_to_name
from .exceptions import ParseError, SimpleParseError, MultipleParseErrors
from ._swagger_utils import Schema as _Schema
from ._swagger_utils import OpenAPISchema as _OpenAPISchema
from ._swagger_utils import maybe_raise_schema as _maybe_raise_schema

logger = structlog.get_logger()

try:
    import flask
except ImportError:  # pragma: no cover
    pass

LogReplacer = t.Callable[[str, object], object]

_ParserT = t.TypeVar('_ParserT', bound='Parser')

__all__ = (
    'Parser',
    'Union',
    'SimpleValueFactory',
    'SimpleValue',
)


class Parser(t.Generic[_T_COV]):
    """Base class for a parser.
    """
    if _USE_SLOTS:
        __slots__ = (
            '__description',
            '__schema_name',
            '_use_readable_describe',
            '__open_api_metadata',
        )

    def __init__(self) -> None:
        self.__description: Final[t.Optional[str]] = None
        self.__schema_name: Final[t.Optional[t.Tuple[str, object]]] = None
        self._use_readable_describe: Final[bool] = False
        self.__open_api_metadata: Final[t.Optional[t.Mapping[str,
                                                             object]]] = None

    def use_readable_describe(self: _ParserT, readable: bool) -> _ParserT:
        """Enable (or disable) the option to use a more readable version of the
        ``describe`` method.

        This might cause the describe to be slower, so only enable when really
        needed or if the speed doesn't matter.
        """
        if readable == self._use_readable_describe:
            return self

        res = copy.copy(self)
        # We cannot assign to this property normally as it is final.
        # pylint: disable=protected-access
        res._use_readable_describe = readable  # type: ignore[misc]
        return res

    def add_description(self: _ParserT, description: str) -> _ParserT:
        """Add a description to the parser.

        :param description: The description to add.

        :returns: A new parser with the given description.
        """
        res = copy.copy(self)
        # We cannot assign to this property normally as it is final.
        # pylint: disable=protected-access,unused-private-member
        res.__description = description  # type: ignore[misc]
        return res

    def as_schema(self: _ParserT, name: str, typ: object = None) -> _ParserT:
        """Add this parser as a separate model to the OpenAPI spec.

        :param name: The name of the model in the spec.
        """
        if typ is None:
            typ = object()
        res = copy.copy(self)
        # We cannot assign to this property normally as it is final.
        # pylint: disable=protected-access,unused-private-member
        res.__schema_name = (name, typ)  # type: ignore[misc]
        return res

    def add_open_api_metadata(
        self: _ParserT, key: str, value: object
    ) -> _ParserT:
        """Add metadata for open api.

        :param key: The key under which the data should be store.
        :param value: The value that should be stored.
        """
        res = copy.copy(self)
        old_metadata = self.__open_api_metadata
        if old_metadata is None:
            old_metadata = {}
        metadata = {
            **old_metadata,
            key: value,
        }
        # We cannot assign to this property normally as it is final.
        # pylint: disable=protected-access,unused-private-member
        res.__open_api_metadata = metadata  # type: ignore[misc]
        return res

    def maybe_parse(self, value: object) -> cg_maybe.Maybe[_T_COV]:
        """Try to parse the given value, returning ``Nothing`` if parsing
        failed.
        """
        try:
            return cg_maybe.Just(self.try_parse(value))
        except ParseError:
            return cg_maybe.Nothing

    @abc.abstractmethod
    def try_parse(self, value: object) -> _T_COV:
        """Try and parse the given ``value```.

        :param value: The value it should try and parse.

        :returns: The parsed value.

        :raises ParserError: If the value could not be parsed.
        """
        ...

    @abc.abstractmethod
    def describe(self) -> str:
        """Describe this parser, used for error messages.
        """
        ...

    @abc.abstractmethod
    def _to_open_api(self, schema: _OpenAPISchema) -> t.Mapping[str, t.Any]:
        ...

    def to_open_api(self, schema: _OpenAPISchema) -> t.Mapping[str, t.Any]:
        """Convert this parser to an OpenAPI schema.
        """
        res = self._to_open_api(schema)
        if self.__open_api_metadata is not None:
            res = {**res, **self.__open_api_metadata}

        if self.__description is not None:
            desc = schema.make_comment(self.__description)
            if '$ref' in res:
                res = {'description': desc, 'allOf': [res]}
            else:
                res = {**res, 'description': desc}

        if self.__schema_name is None:
            return res
        else:
            name, typ = self.__schema_name
            return schema.add_as_schema(name, res, typ)

    def __or__(
        self: 'Parser[_T]', other: 'Parser[_Y]'
    ) -> 'Parser[t.Union[_T, _Y]]':
        return Union(self, other)

    def __generate_schema(self, open_api: _OpenAPISchema) -> _Schema:
        json_schema = self.to_open_api(open_api)
        return _Schema(typ='application/json', schema=json_schema)

    def from_flask(self, *, log_replacer: LogReplacer = None) -> _T_COV:
        """Parse the data from the current flask request.

        :param log_replacer: See :meth:`Parser.try_parse_and_log`.

        :returns: The parsed json from the current flask request.
        """
        _maybe_raise_schema(self.__generate_schema)
        json = flask.request.get_json()
        return self.try_parse_and_log(json, log_replacer=log_replacer)

    def try_parse_and_log(
        self,
        json: object,
        *,
        log_replacer: LogReplacer = None,
        msg: str = 'JSON request processed',
    ) -> _T_COV:
        """Log and try to parse the given ``json``

        :param json: The object you want to try and parse.
        :param log_replacer: This function will be used to remove any sensitive
            data from the json before logging.

        :returns: The parsed data.
        """
        if log_replacer is None:
            logger.info(msg, request_data=json)
        elif isinstance(json, dict):
            to_log = {k: log_replacer(k, v) for k, v in json.items()}
            logger.info(msg, request_data=to_log)
        else:
            # The replacers are used for top level objects, in this case it is
            # better to be extra sure we don't log passwords so simply the
            # type.
            logger.info(
                msg,
                request_data='<FILTERED>',
                request_data_type=type_to_name(type(json)),
            )

        try:
            return self.try_parse(json)
        except ParseError as exc:
            if log_replacer is None:
                raise exc
            # Don't do ``from exc`` as that might leak the value
            raise SimpleParseError(  # pylint: disable=raise-missing-from
                self,
                '<REDACTED>',
                extra={
                    'message': (
                        'we cannot show you as this data should contain'
                        ' confidential information, but the input value was of'
                        ' type {}'
                    ).format(type(json))
                }
            )


class Union(t.Generic[_T, _Y], Parser[t.Union[_T, _Y]]):
    """A parser that is a union between two parsers.
    """
    if _USE_SLOTS:
        __slots__ = ('_parser', )

    def use_readable_describe(
        self: 'Union[_T, _Y]', readable: bool
    ) -> 'Union[t.Union[_T, _Y], _Y]':
        res = super().use_readable_describe(readable)
        res._parser = res._parser.use_readable_describe(readable)  # pylint: disable=protected-access
        return res

    def __init__(self, first: Parser[_T], second: Parser[_Y]) -> None:
        super().__init__()
        from ._mapping import \
            DiscriminatedUnion  # pylint: disable=import-outside-toplevel

        self._parser: Parser[t.Union[_T, _Y]]
        if isinstance(first, Union):
            first = first._parser

        if isinstance(second, Union):
            second = second._parser

        sub_parsers: t.Sequence[Parser[t.Union[_T, _Y]]] = (first, second)
        maybe_parser = DiscriminatedUnion.maybe_create(sub_parsers)
        if maybe_parser.is_just:
            self._parser = maybe_parser.value
        elif (
            isinstance(first, SimpleValueFactory) and
            isinstance(second, SimpleValueFactory)
        ):
            self._parser = _SimpleUnion(first.typ, second.typ)
        elif (
            isinstance(first, _SimpleUnion) and
            isinstance(second, SimpleValueFactory)
        ):
            self._parser = _SimpleUnion(*first.typs, second.typ)
        elif (
            isinstance(first, SimpleValueFactory) and
            isinstance(second, _SimpleUnion)
        ):
            self._parser = _SimpleUnion(first.typ, *second.typs)
        elif (
            isinstance(first, _SimpleUnion) and
            isinstance(second, _SimpleUnion)
        ):
            self._parser = _SimpleUnion(*first.typs, *second.typs)
        else:
            parser: cg_maybe.Maybe[Parser[t.Union[_T, _Y]]] = cg_maybe.Nothing
            if isinstance(first, DiscriminatedUnion):
                parser = first.maybe_add(second)
            elif isinstance(second, DiscriminatedUnion):
                parser = second.maybe_add(first)
            self._parser = parser.or_default_lazy(
                lambda: _RichUnion(first, second)
            )

    def describe(self) -> str:
        return self._parser.describe()

    def _to_open_api(self, schema: _OpenAPISchema) -> t.Mapping[str, t.Any]:
        res = self._parser.to_open_api(schema)
        if 'anyOf' in res:
            res = {**res, 'anyOf': schema.expand_anyof(res['anyOf'])}
        return res

    def try_parse(self, value: object) -> t.Union[_T, _Y]:
        return self._parser.try_parse(value)


_SimpleValueT = t.TypeVar('_SimpleValueT', str, int, float, bool)


class SimpleValueFactory(t.Generic[_SimpleValueT], Parser[_SimpleValueT]):
    """Create a parser for a simple type.
    """
    if _USE_SLOTS:
        __slots__ = ('typ', )

    def describe(self) -> str:
        return type_to_name(self.typ)

    def __init__(self, typ: t.Type[_SimpleValueT]) -> None:
        super().__init__()
        self.typ: Final[t.Type[_SimpleValueT]] = typ

    def _to_open_api(self, schema: _OpenAPISchema) -> t.Mapping[str, t.Any]:
        return {'type': schema.simple_type_to_open_api_type(self.typ)}

    def try_parse(self, value: object) -> _SimpleValueT:
        # Local access is faster, so 'cache' the value here.
        typ = self.typ

        # Don't allow booleans as integers
        if isinstance(value, bool) and typ != bool:
            raise SimpleParseError(self, found=value)
        if isinstance(value, typ):
            return value
        # Also allow integers as floats
        if typ is float and isinstance(value, int):
            return float(value)  # type: ignore
        raise SimpleParseError(self, found=value)


class SimpleValue:
    """A collection of validators for primitive values.
    """
    int = SimpleValueFactory(int)
    float = SimpleValueFactory(float)
    str = SimpleValueFactory(str)
    bool = SimpleValueFactory(bool)


_SimpleUnionT = t.TypeVar(
    '_SimpleUnionT', bound=t.Union[str, int, float, bool]
)


class _SimpleUnion(t.Generic[_SimpleUnionT], Parser[_SimpleUnionT]):
    if _USE_SLOTS:
        __slots__ = ('typs', )

    def __init__(self, *typs: t.Type[_SimpleUnionT]) -> None:
        super().__init__()
        self.typs: Final[t.Tuple[t.Type[_SimpleUnionT], ...]] = typs

    def describe(self) -> str:
        return 'Union[{}]'.format(', '.join(map(type_to_name, self.typs)))

    def _to_open_api(self, schema: _OpenAPISchema) -> t.Mapping[str, t.Any]:
        return {
            'anyOf': [{
                'type':
                    schema.simple_type_to_open_api_type(t.cast(t.Type, typ))
            } for typ in self.typs]
        }

    def _raise(self, value: object) -> t.NoReturn:
        raise SimpleParseError(
            self,
            value,
            extra={
                'message':
                    '(which is of type {})'.format(type_to_name(type(value)))
            }
        )

    def try_parse(self, value: object) -> _SimpleUnionT:
        # Don't allow booleans as integers
        if isinstance(value, bool) and bool not in self.typs:
            self._raise(value)
        if isinstance(value, self.typs):
            return value  # type: ignore
        # Also allow integers as floats
        if float in self.typs and isinstance(value, int):
            return float(value)  # type: ignore
        return self._raise(value)


class _RichUnion(t.Generic[_T, _Y], Parser[t.Union[_T, _Y]]):
    if _USE_SLOTS:
        __slots__ = ('__first', '__second')

    def __init__(self, first: Parser[_T], second: Parser[_Y]) -> None:
        super().__init__()
        self.__first = first
        self.__second = second

    def describe(self) -> str:
        if self._use_readable_describe:
            import textwrap  # pylint: disable=import-outside-toplevel

            def _find_parts(cur: Parser) -> t.List[str]:
                if isinstance(cur, type(self)):
                    return [
                        *_find_parts(cur.__first),  # pylint: disable=protected-access
                        *_find_parts(cur.__second),  # pylint: disable=protected-access
                    ]
                else:
                    return [cur.describe()]

            indent = ' ' * 4
            return 'Union[\n{},\n]'.format(
                ',\n'.join(
                    textwrap.indent(part, indent)
                    for part in _find_parts(self)
                )
            )
        else:
            first = self.__first.describe()
            second = self.__second.describe()
            return 'Union[{}, {}]'.format(first, second)

    def _to_open_api(self, schema: _OpenAPISchema) -> t.Mapping[str, t.Any]:
        return {
            'anyOf': [
                self.__first.to_open_api(schema),
                self.__second.to_open_api(schema)
            ]
        }

    def try_parse(self, value: object) -> t.Union[_T, _Y]:
        try:
            return self.__first.try_parse(value)
        except ParseError as first_err:
            try:
                return self.__second.try_parse(value)
            except ParseError as second_err:
                raise MultipleParseErrors(  # pylint: disable=raise-missing-from
                    self,
                    value,
                    errors=[first_err, second_err]
                )
