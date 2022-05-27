"""This module contains parsers for various kinds of mappings.
"""
import abc
import copy
import enum
import typing as t
import inspect

import cg_maybe

from ._base import Parser, SimpleValue
from ._enum import StringEnum
from ._utils import USE_SLOTS as _USE_SLOTS
from ._utils import T as _T
from ._utils import Y as _Y
from ._utils import Final, TypedDict
from .exceptions import ParseError, SimpleParseError, MultipleParseErrors
from ._swagger_utils import OpenAPISchema

__all__ = (
    'RequiredArgument',
    'OptionalArgument',
    'DefaultArgument',
    'OnExtraAction',
    'BaseFixedMapping',
    'FixedMapping',
    'LookupMapping',
)


class _BaseDict(TypedDict):
    pass


_Key = t.TypeVar('_Key', bound=str)
_BaseDictT = t.TypeVar('_BaseDictT', bound=_BaseDict)


class _Argument(t.Generic[_T, _Key]):
    if _USE_SLOTS:
        __slots__ = ('key', 'value', 'doc')

    def __init__(
        self,
        key: _Key,
        value: Parser[_T],
        doc: str,
    ) -> None:
        self.key: Final = key
        self.value: Final = value
        self.doc: Final = doc

    @abc.abstractmethod
    def describe(self) -> str:
        """Describe this argument.
        """
        ...

    @abc.abstractmethod
    def try_parse(self, value: t.Mapping[str, object]) -> t.Any:
        """Parse this argument.
        """
        ...

    def to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        """Convert this argument to open api.
        """
        # We save a copy in the common case here, as never call this method
        # when running the server, and adding a description copies the parser.
        return self.value.add_description(self.doc).to_open_api(schema)

    def _try_parse(self, value: t.Mapping[str, object]) -> cg_maybe.Maybe[_T]:
        if self.key not in value:
            return cg_maybe.Nothing

        found = value[self.key]
        try:
            return cg_maybe.Just(self.value.try_parse(found))
        except ParseError as err:
            raise err.add_location(self.key) from err


class RequiredArgument(t.Generic[_T, _Key], _Argument[_T, _Key]):
    """An argument in a ``FixedMapping`` that is required to be present.
    """
    def describe(self) -> str:
        return f'{self.key}: {self.value.describe()}'

    def try_parse(self, value: t.Mapping[str, object]) -> _T:
        """Try to parse this required argument from the given mapping.
        """
        res = self._try_parse(value)
        if isinstance(res, cg_maybe.Just):
            return res.value
        raise SimpleParseError(self.value,
                               cg_maybe.Nothing).add_location(self.key)


class DefaultArgument(t.Generic[_T, _Key], _Argument[_T, _Key]):
    """An argument in a ``FixedMapping`` that doesn't have to be present.
    """
    if _USE_SLOTS:
        __slots__ = ('__default', )

    def __init__(
        self,
        key: _Key,
        value: Parser[_T],
        doc: str,
        *,
        default: t.Callable[[], _T],
    ) -> None:
        super().__init__(key, value, doc)
        self.__default: Final = default

    def describe(self) -> str:
        return f'{self.key}?: {self.value.describe()}'

    def try_parse(self, value: t.Mapping[str, object]) -> _T:
        """Try to parse this required argument from the given mapping.
        """
        return self._try_parse(value).or_default_lazy(self.__default)

    def to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        """Convert this argument to open api.
        """
        return {
            **super().to_open_api(schema),
            'default': self.__default(),
        }


class OptionalArgument(t.Generic[_T, _Key], _Argument[_T, _Key]):
    """An argument in a ``FixedMapping`` that doesn't have to be present.
    """
    def describe(self) -> str:
        return f'{self.key}?: {self.value.describe()}'

    def try_parse(self, value: t.Mapping[str, object]) -> cg_maybe.Maybe[_T]:
        return self._try_parse(value)


class _DictGetter(t.Generic[_BaseDictT]):
    if _USE_SLOTS:
        __slots__ = ('__data', )

    def __init__(self, data: _BaseDictT) -> None:
        self.__data = data

    if not t.TYPE_CHECKING:

        def _unsafe_get_base_data(self) -> t.Dict[str, t.Any]:
            return copy.copy(self.__data)

    def __repr__(self) -> str:
        return '_DictGetter({!r})'.format(self.__data)

    def __getattr__(self, key: str) -> object:
        try:
            return self.__data[key]  # type: ignore[literal-required]
        except KeyError:
            return super().__getattribute__(key)


_BaseFixedMappingT = t.TypeVar('_BaseFixedMappingT', bound='_BaseFixedMapping')


class OnExtraAction(enum.Enum):
    """Action to perform if a :class:`_BaseFixedMapping` finds keys in the
    dictionary it is parsing that were not defined on the parser.
    """
    nothing = enum.auto()
    warning = enum.auto()
    error = enum.auto()


class _BaseFixedMapping(t.Generic[_BaseDictT]):
    def __init__(self, arguments: t.Sequence[_Argument]) -> None:
        super().__init__()
        self._arguments = arguments
        self._on_extra = OnExtraAction.nothing

    def set_on_extra(
        self: _BaseFixedMappingT, value: OnExtraAction
    ) -> _BaseFixedMappingT:
        """Enable warnings or errors when extra keys are found in the
        dictionaries to parse.
        """
        res = copy.copy(self)
        res._on_extra = value  # pylint: disable=protected-access
        return res

    @abc.abstractmethod
    def describe(self) -> str:
        """Describe this parser.
        """
        raise NotImplementedError

    def _describe(self, readable: bool) -> str:
        if readable and len(list(self._arguments)) > 1:
            import textwrap  # pylint: disable=import-outside-toplevel

            args = [
                arg.describe()
                for arg in sorted(self._arguments, key=lambda a: a.key)
            ]
            indent = ' ' * 4
            content = '\n{},\n'.format(
                ',\n'.join(textwrap.indent(arg, indent) for arg in args)
            )
        else:
            args = [arg.describe() for arg in self._arguments]
            content = ', '.join(args)
        return 'Mapping[{}]'.format(content)

    def to_open_api_as_query(
        self, schema: OpenAPISchema
    ) -> t.Sequence[t.Mapping[str, t.Any]]:
        """Convert this mapping to a OpenAPI object as if it were used as a
        query string.
        """
        return [{
            'in': 'query',
            'name': arg.key,
            'schema': arg.to_open_api(schema),
            'description': schema.make_comment(arg.doc),
            'required': isinstance(arg, RequiredArgument),
        } for arg in self._arguments]

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        required = [
            arg.key for arg in self._arguments
            if isinstance(arg, RequiredArgument)
        ]
        res = {
            'type': 'object',
            'properties': {
                arg.key: arg.to_open_api(schema)
                for arg in self._arguments
            },
        }
        if required:
            res['required'] = required
        return res

    def _try_parse(
        self,
        value: object,
    ) -> _BaseDictT:
        if not isinstance(value, dict):
            raise SimpleParseError(self, value)

        result = {}
        errors = []
        for arg in self._arguments:
            try:
                result[arg.key] = arg.try_parse(value)
            except ParseError as exc:
                errors.append(exc)

        if errors:
            raise MultipleParseErrors(self, value, errors)

        extra_keys = value.keys() - result.keys()
        if extra_keys:
            if self._on_extra is OnExtraAction.warning:
                import warnings  # pylint: disable=import-outside-toplevel
                warnings.warn(
                    'Got extra keys: {}'.format(extra_keys),
                    stacklevel=3,
                )
            elif self._on_extra is OnExtraAction.error:
                extra_keys_str = ', '.join(extra_keys)
                raise SimpleParseError(
                    self,
                    value,
                    extra={
                        'extra_keys': extra_keys_str,
                        'message': f'Got extra keys: {extra_keys_str}',
                    }
                )

        return t.cast(_BaseDictT, result)


class BaseFixedMapping(
    t.Generic[_BaseDictT], _BaseFixedMapping[_BaseDictT], Parser[_BaseDictT]
):
    """A fixed mapping that returns a dictionary instead of a ``_DictGetter``.

    .. note::

        You should only create this using
        :meth:`.BaseFixedMapping.from_typeddict`, not using the normal
        constructor.
    """
    def __init__(
        self,
        *arguments: object,
        schema: t.Optional[t.Type[_BaseDictT]],
    ) -> None:
        super().__init__(t.cast(t.Any, arguments))
        self.__has_optional = any(
            isinstance(arg, OptionalArgument) for arg in self._arguments
        )
        self._schema: t.Optional[t.Type[_BaseDictT]] = schema

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        if self._schema is None:
            return super()._to_open_api(schema)
        else:
            return schema.add_schema(self._schema)

    def describe(self) -> str:
        return self._describe(self._use_readable_describe)

    def try_parse(self, value: object) -> _BaseDictT:
        res = self._try_parse(value)
        # Optional values are parsed as Maybe, but callers think they will
        # simply get a dict with possibly missing items. So we convert that
        # here.
        if not self.__has_optional:
            return res

        for arg in self._arguments:
            if not isinstance(arg, OptionalArgument):
                continue

            key = arg.key
            val = res[key]  # type: ignore[literal-required]
            if cg_maybe.Nothing.is_nothing_instance(val):
                del res[key]
            else:
                assert isinstance(val, cg_maybe.Just)
                res[key] = val.value  # type: ignore

        return res

    @classmethod
    def from_function_parameters_list(
        cls,
        params: t.Iterable[inspect.Parameter],
        from_query: bool,
    ) -> 'BaseFixedMapping[t.Any]':
        """Create a BaseFixedMapping from a list of function parameters.
        """
        # pylint: disable=import-outside-toplevel
        from ._convert import ConvertCtx

        args = []
        for param in params:
            sub_parser = ConvertCtx(param.annotation, from_query,
                                    False).convert()
            if param.default == inspect.Parameter.empty:
                args.append(
                    RequiredArgument(  # type: ignore
                        param.name,
                        sub_parser,
                        ''
                    )
                )
            else:
                default = param.default

                args.append(
                    DefaultArgument(  # type: ignore
                        param.name,
                        sub_parser,
                        '',
                        default=t.cast(
                            t.Callable,
                            lambda _default=default: _default,
                        ),
                    )
                )
        return BaseFixedMapping(  # type: ignore
            *args, schema=None
        )

    @classmethod
    def from_function(cls, fun: t.Callable) -> 'BaseFixedMapping[t.Any]':
        """Create a mapping from a function signature.
        """
        return cls.from_function_parameters_list(
            inspect.signature(fun).parameters.values(),
            from_query=False,
        )

    @classmethod
    def from_typeddict(
        cls,
        typeddict: t.Type,
        *,
        readable: bool = False
    ) -> 'BaseFixedMapping[t.Any]':
        """Create a mapping from an existing typeddict.
        """
        # pylint: disable=import-outside-toplevel
        from ._convert import ConvertCtx
        res = ConvertCtx(typeddict, False, readable=readable).convert()
        return t.cast(BaseFixedMapping[t.Any], res)


class FixedMapping(
    t.Generic[_BaseDictT], _BaseFixedMapping[_BaseDictT],
    Parser[_DictGetter[_BaseDictT]]
):
    """A mapping in which the keys are fixed and the values can have different
    types.
    """
    def __init__(self, *arguments: object) -> None:
        super().__init__(t.cast(t.Any, arguments))
        self.__tag: t.Optional[t.Tuple[str, object]] = None

    def describe(self) -> str:
        return self._describe(self._use_readable_describe)

    def add_tag(self, key: str, value: object) -> 'FixedMapping[_BaseDictT]':
        """Add a tag to this mapping.

        This tag will always be added to the final mapping after parsing.

        :param key: The key of the tag, should be a literal string.
        :param value: The value of the tag, should be a literal string.

        :returns: The existing mapping but mutated.
        """
        self.__tag = (key, value)
        return self

    def try_parse(
        self,
        value: object,
    ) -> _DictGetter[_BaseDictT]:
        result = self._try_parse(value)

        if self.__tag is not None:
            result[self.__tag[0]  # type: ignore[literal-required]
                   ] = self.__tag[1]
        return _DictGetter(result)

    def combine(
        self, other: 'FixedMapping[t.Any]'
    ) -> 'FixedMapping[_BaseDict]':
        """Combine this fixed mapping with another.

        :param other: The mapping to combine with. The arguments are not
            allowed to overlap

        :returns: A new fixed mapping with arguments of both given mappings.
        """
        args = [*self._arguments, *other._arguments]  # pylint: disable=protected-access
        return FixedMapping(*args)  # type: ignore

    @classmethod
    def make_discriminated_union(
        cls,
        discriminator: str,
        *parsers: 'FixedMapping[t.Any]',
    ) -> 'DiscriminatedUnion[t.Any]':
        """Make a discriminated union based on a given discriminator.

        :param discriminator: The key to be used as the discriminator.
        :param parsers: The list of parsers to use for the union. Each parser
            should map ``discriminator`` to a unique string literal.

        :returns: The created union.
        """
        def get_value(parser: FixedMapping) -> str:
            for arg in parser._arguments:  # pylint: disable=protected-access
                if arg.key == discriminator:
                    assert isinstance(arg, RequiredArgument)
                    assert isinstance(arg.value, StringEnum)
                    assert len(arg.value.opts) == 1
                    return next(iter(arg.value.opts))
            assert False

        lookup = {get_value(parser): parser for parser in parsers}
        return DiscriminatedUnion(discriminator, lookup)


class LookupMapping(t.Generic[_T], Parser[t.Mapping[str, _T]]):
    """A parser that implements a lookup mapping.

    This a mapping where the keys are not fixed, so only the values are parsed
    (and are all parsed the same). Currently only string keys are allowed.
    """
    if _USE_SLOTS:
        __slots__ = ('__parser', )

    _PARSE_KEY = SimpleValue.str

    def __init__(self, parser: Parser[_T]) -> None:
        super().__init__()
        self.__parser = parser

    def describe(self) -> str:
        return 'Mapping[str: {}]'.format(self.__parser.describe())

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        return {
            'type': 'object',
            'additionalProperties': self.__parser.to_open_api(schema),
        }

    def try_parse(self, value: object) -> t.Mapping[str, _T]:
        if not isinstance(value, dict):
            raise SimpleParseError(self, value)

        result = {}
        errors = []
        for key, val in value.items():
            try:
                parsed_key = self._PARSE_KEY.try_parse(key)
                result[parsed_key] = self.__parser.try_parse(val)
            except ParseError as exc:
                errors.append(exc.add_location(str(key)))
        if errors:
            raise MultipleParseErrors(self, value, errors)

        return result


class DiscriminatedUnion(t.Generic[_T], Parser[_T]):
    """A union of mappings discriminated by a single key.
    """
    if _USE_SLOTS:
        __slots__ = ('__discriminator', '__parser_lookup', '__key_parser')

    def __init__(
        self,
        discriminator: str,
        parser_lookup: t.Mapping[str, Parser[_T]],
    ) -> None:
        super().__init__()
        self.__discriminator = discriminator
        self.__parser_lookup = parser_lookup
        self.__key_parser = StringEnum(*parser_lookup.keys())  # type: ignore

    def maybe_merge(
        self, other: 'DiscriminatedUnion[_Y]'
    ) -> cg_maybe.Maybe['DiscriminatedUnion[t.Union[_T, _Y]]']:
        """Try to merge two discriminated unions.

        :param other: The other discriminated union to add.

        :returns: A new discriminated union, if it could be created.
        """
        parsers: t.Sequence[Parser[t.Union[_T, _Y]]] = (
            *self.__parser_lookup.values(),
            *other.__parser_lookup.values(),  # pylint: disable=protected-access
        )
        return DiscriminatedUnion.maybe_create(parsers)

    def maybe_add(
        self,
        parser: Parser[_Y],
    ) -> cg_maybe.Maybe['DiscriminatedUnion[t.Union[_T, _Y]]']:
        """Maybe add a parser to this discriminated union.

        :param parser: The parser to add.

        :returns: A new discriminated union, if it could be created.
        """
        maybe_other: cg_maybe.Maybe[DiscriminatedUnion[_Y]]
        if isinstance(parser, DiscriminatedUnion):
            maybe_other = cg_maybe.Just(parser)
        else:
            maybe_other = DiscriminatedUnion.maybe_create((parser, ))

        return maybe_other.chain(self.maybe_merge)

    @classmethod
    def maybe_create(
        cls, parsers: t.Sequence[Parser[_T]]
    ) -> cg_maybe.Maybe['DiscriminatedUnion[_T]']:
        """Try to create a discriminated union from a list of parsers.

        :param parses: The parsers to create a discriminated union from.

        :returns: Maybe the create union.
        """
        if not parsers:
            return cg_maybe.Nothing

        first, *rest = parsers
        if not isinstance(first, (BaseFixedMapping, FixedMapping)):
            return cg_maybe.Nothing

        def _is_possible(arg: _Argument) -> t.Sequence[str]:
            if (
                isinstance(arg, RequiredArgument) and
                isinstance(arg.value, StringEnum) and
                arg.value.str_parser is SimpleValue.str and
                len(arg.value.opts) == 1
            ):
                return (next(iter(arg.value.opts)), )
            return ()

        arguments = first._arguments  # pylint: disable=protected-access
        possible_keys = {
            arg.key: {value: first}
            for arg in arguments for value in _is_possible(arg)
        }
        for parser in rest:
            if not isinstance(parser, (BaseFixedMapping, FixedMapping)):
                return cg_maybe.Nothing

            found_any = False

            for arg in parser._arguments:  # pylint: disable=protected-access
                vals = possible_keys.get(arg.key)
                if vals is None:
                    continue
                new_opt = _is_possible(arg)
                # The arg is not valid or we found a duplicate value.
                if not new_opt or new_opt[0] in vals:
                    del possible_keys[arg.key]
                else:
                    vals[new_opt[0]] = parser
                    found_any = True
            if not found_any:
                return cg_maybe.Nothing

        if not possible_keys:
            return cg_maybe.Nothing
        discriminator, parser_lookup = list(possible_keys.items())[0]
        return cg_maybe.Just(cls(discriminator, parser_lookup))

    def describe(self) -> str:
        if self._use_readable_describe:
            import textwrap  # pylint: disable=import-outside-toplevel

            def indent(part: str) -> str:
                return textwrap.indent(part, '    ')

            maybe_newline = '\n'
        else:

            def indent(part: str) -> str:
                return part

            maybe_newline = ''

        return 'Union[{maybe_newline}{parts},{maybe_newline}]'.format(
            maybe_newline=maybe_newline,
            parts=f',{maybe_newline}'.join(
                indent(part.describe())
                for part in self.__parser_lookup.values()
            )
        )

    def _to_open_api(self, schema: OpenAPISchema) -> t.Mapping[str, t.Any]:
        mapping = {}
        for name, parser in self.__parser_lookup.items():
            sub = parser.to_open_api(schema)
            if '$ref' not in sub:
                if 'x-model-name' not in sub:  # pragma: no cover
                    raise AssertionError((
                        f'Expected to find x-model-name in {sub} but did not'
                        f' find it.'
                    ))
                sub = schema.add_as_schema(sub['x-model-name'], sub, parser)
            mapping[name] = sub['$ref']
        return {
            'oneOf': [{'$ref': sub} for sub in mapping.values()],
            'discriminator': {
                'propertyName': self.__discriminator,
                'mapping': mapping,
            },
        }

    def try_parse(self, value: object) -> _T:
        if not isinstance(value, dict):
            raise SimpleParseError(self, value)
        if self.__discriminator not in value:
            raise SimpleParseError(self, value)
        disc_value = self.__key_parser.try_parse(value[self.__discriminator])
        return self.__parser_lookup[disc_value].try_parse(value)
