"""This module contains the logic to convert python types into parsers.
"""
import enum
import uuid
import typing as t
import decimal
import datetime
import collections
import dataclasses

from cg_dt_utils import DatetimeWithTimezone

from ._base import Parser, SimpleValue
from ._enum import EnumValue, StringEnum
from ._lazy import Lazy
from ._list import List, TwoTuple
from ._query import QueryParam
from ._utils import USE_SLOTS, Literal, is_typeddict
from ._literal import LiteralBoolean
from ._mapping import (
    LookupMapping, BaseFixedMapping, OptionalArgument, RequiredArgument,
    DiscriminatedUnion
)
from ._nullable import Nullable
from ._any_value import AnyValue
from ._rich_value import RichValue


class _SkipConverter(Exception):
    if USE_SLOTS:
        __slots__ = ()


_ConvertPriority = t.NewType('_ConvertPriority', int)


@dataclasses.dataclass(frozen=True, eq=True, order=True)
class ConvertPriority:
    """The priority of a convert, the higher the earlier it will be called.
    """
    if USE_SLOTS:
        __slots__ = ('_prio', )
    _prio: _ConvertPriority

    @classmethod
    def high(cls) -> 'ConvertPriority':
        """Default high priority.
        """
        return cls(_ConvertPriority(1000))

    @classmethod
    def default(cls) -> 'ConvertPriority':
        """Default priority.
        """
        return cls(_ConvertPriority(0))

    def increase(self) -> 'ConvertPriority':
        """Increase the priority.
        """
        return ConvertPriority(_ConvertPriority(self._prio + 1))

    def decrease(self) -> 'ConvertPriority':
        """Decrease the priority.
        """
        return ConvertPriority(_ConvertPriority(self._prio - 1))


class _RecursiveManager:
    _PARSERS: t.Dict[t.Type, Parser[t.Any]] = {}
    _DOING: t.Set[t.Type] = set()
    _SHOULD_ADD: t.Set[t.Type] = set()

    @classmethod
    def recurse(cls, ctx: 'ConvertCtx', typ: t.Type) -> Parser:
        """Convert the given ``typ`` with the given ``ctx`` while handling
        recursive parsers.
        """
        if typ in cls._DOING:
            cls._SHOULD_ADD.add(typ)
            return Lazy(lambda: cls._PARSERS[typ])
        else:
            cls._DOING.add(typ)
            res = ctx.update_type(typ).convert()
            cls._DOING.remove(typ)

            if typ in cls._SHOULD_ADD:
                cls._PARSERS[typ] = res
                cls._SHOULD_ADD.remove(typ)

            return res


@dataclasses.dataclass(frozen=True)
class ConvertCtx:
    """A context object for the type we are currently converting.
    """
    #: The type we are converting.
    typ: t.Type
    #: Are converting for a query.
    from_query: bool = dataclasses.field(default=False)
    #: Was a readable parser requested?
    readable: bool = dataclasses.field(default=False)
    #: Extra data you can store stuff in. Use ``add_extra_data`` to mutate
    #: this.
    extra_data: t.Mapping[str, t.Any] = dataclasses.field(default_factory=dict)
    #: Evaluate type annotation strings. This only has effect on python > 3.10
    eval_type_annotations: bool = dataclasses.field(default=False)

    _prev_typs: t.Tuple[t.Type, ...] = dataclasses.field(default_factory=tuple)

    @property
    def origin(self) -> t.Optional[t.Any]:
        """The ``__origin__`` attribute of ``typ`` if present.
        """
        return getattr(self.typ, '__origin__', None)

    def add_extra_data(self, key: str, value: t.Any) -> 'ConvertCtx':
        """Create a new context with the ``value`` added to ``extra_data``.

        :param key: The key to store the data under.
        :param value: The value to store.
        """
        return ConvertCtx(
            typ=self.typ,
            from_query=self.from_query,
            readable=self.readable,
            extra_data={**self.extra_data, key: value},
            _prev_typs=self._prev_typs,
        )

    def update_type(self, new_typ: t.Type) -> 'ConvertCtx':
        """Change the type of the context.

        :param new_type: The new type of the context.
        """
        return ConvertCtx(
            typ=new_typ,
            from_query=self.from_query,
            readable=self.readable,
            extra_data=self.extra_data,
            _prev_typs=(*self._prev_typs, self.typ),
        )

    def assert_not_query(self, cond: bool = False) -> None:
        """Assert we are not in a query.
        """
        if self.from_query and not cond:  # pragma: no cover
            self.assert_false(
                '{} is not supported as query param'.format(self.typ)
            )

    def skip(self) -> t.NoReturn:  # pylint: disable=no-self-use
        """Use a different converter for this type.
        """
        raise _SkipConverter

    def recurse_with_guard(self, new_typ: t.Type) -> Parser:
        """Convert the given ``new_typ`` with guards in-place to deal with
        recursion.
        """
        return _RecursiveManager.recurse(self, new_typ)

    def convert(self) -> Parser:
        """Convert this context into a parser.
        """
        for _, check, convert in _CONVERTERS:
            if check(self):
                new_self = ConvertCtx(
                    typ=self.typ,
                    from_query=self.from_query,
                    readable=self.readable,
                    extra_data=self.extra_data,
                    _prev_typs=self._prev_typs,
                )
                try:
                    return convert(new_self)
                except _SkipConverter:
                    pass
        self.assert_false('No coverter for this type')

    def assert_false(self, msg: str) -> t.NoReturn:
        """Raise an ``AssertionError`` with some extra context.
        """
        prev_path = ".".join(map(str, self._prev_typs))
        raise AssertionError(
            f'Error when converting {self.typ}: {msg} (origin: {self.origin})'
            f' (path: {prev_path})'
        )


Checker = t.Callable[[ConvertCtx], bool]
Converter = t.Callable[[ConvertCtx], Parser]
_CONVERTERS: t.List[t.Tuple[ConvertPriority, Checker, Converter]] = []


def as_converter(
    checker: Checker,
    priority: ConvertPriority = ConvertPriority.default(),
) -> t.Callable[[Converter], Converter]:
    """Register a function as a convert to create a parser for a type.

    :param checker: A function that checks if this converter should be used for
        the type.
    :param priority: The priority of the checker. The higher it is the earlier
        the registered function will be called.
    """
    def _wrapper(converter: Converter) -> Converter:
        _CONVERTERS.append((priority, checker, converter))
        _CONVERTERS.sort(key=lambda el: el[0], reverse=True)
        return converter

    return _wrapper


def remove_converter(converter: Converter) -> None:
    """Unregister the given converter.

    :param converter: The convert to unregister.
    """
    global _CONVERTERS  # pylint: disable=global-statement
    _CONVERTERS = [c for c in _CONVERTERS if c[-1] != converter]


def _get_args_typeddict(
    ctx: ConvertCtx,
    get_doc: t.Callable[[str], str] = lambda _: '',
) -> t.Sequence[t.Union[RequiredArgument, OptionalArgument]]:
    args: t.List[t.Union[RequiredArgument, OptionalArgument]] = []
    annotations = t.get_type_hints(ctx.typ)

    for key, subtyp in annotations.items():
        sub_parse = ctx.recurse_with_guard(subtyp)
        doc = get_doc(key)
        if key in ctx.typ.__required_keys__:
            args.append(
                RequiredArgument(key, sub_parse, doc)  # type: ignore[misc]
            )
        else:
            args.append(
                OptionalArgument(key, sub_parse, doc)  # type: ignore[misc]
            )
    return args


@as_converter(lambda x: is_typeddict(x.typ))
def _convert_typeddict(ctx: ConvertCtx) -> Parser:
    ctx.assert_not_query()
    args = _get_args_typeddict(ctx)
    mapping = BaseFixedMapping(*args, schema=ctx.typ)  # type: ignore[misc]
    return mapping.use_readable_describe(ctx.readable)


@as_converter(
    lambda x: x.typ in (str, int, bool, float),
    priority=ConvertPriority.high()
)
def _convert_simple(ctx: ConvertCtx) -> Parser:
    if ctx.from_query:
        return getattr(QueryParam, ctx.typ.__name__)
    else:
        return getattr(SimpleValue, ctx.typ.__name__)


@as_converter(lambda x: x.origin in (list, collections.abc.Sequence))
def _convert_list(ctx: ConvertCtx) -> Parser:
    ctx.assert_not_query()
    return List(
        ctx.update_type(ctx.typ.__args__[0]).convert(),
    ).use_readable_describe(ctx.readable)


@as_converter(lambda x: x.origin == t.Union)
def _convert_union(ctx: ConvertCtx) -> Parser:
    typ = ctx.typ
    has_none = type(None) in typ.__args__
    ctx.assert_not_query(not has_none)

    NoneType = type(None)
    non_nullable = [a for a in typ.__args__ if a != NoneType]
    parsers = [
        ctx.update_type(sub_type).convert() for sub_type in non_nullable
    ]
    discriminated = DiscriminatedUnion.maybe_create(parsers)
    res: Parser
    if discriminated.is_just:
        res = discriminated.value
    else:
        res, *rest = parsers
        for item in rest:
            res = res | item
    return Nullable(res) if has_none else res


@as_converter(
    lambda x: x.typ == decimal.Decimal, priority=ConvertPriority.high()
)
def _convert_decimal(_: ConvertCtx) -> Parser:
    return RichValue.Decimal


@as_converter(
    lambda x: (
        x.origin == Literal and len(x.typ.__args__) == 1 and
        isinstance(x.typ.__args__[0], bool)
    ),
    priority=ConvertPriority.high(),
)
def _convert_bool_literal(ctx: ConvertCtx) -> Parser:
    return LiteralBoolean(ctx.typ.__args__[0])  # type: ignore[misc]


@as_converter(
    lambda x: (
        x.origin == Literal and
        all(isinstance(arg, str) for arg in x.typ.__args__)
    ),
    priority=ConvertPriority.high(),
)
def _convert_string_literal(ctx: ConvertCtx) -> Parser:
    typ_args = ctx.typ.__args__
    enum_vals: StringEnum[t.Any] = StringEnum(*typ_args)  # type: ignore[misc]
    return enum_vals.use_readable_describe(ctx.readable)


@as_converter(
    lambda x: isinstance(x.typ, enum.EnumMeta),
    priority=ConvertPriority.high()
)
def _convert_enum(ctx: ConvertCtx) -> Parser:
    return EnumValue(ctx.typ).use_readable_describe(ctx.readable)


@as_converter(
    lambda x: x.origin in (dict, collections.abc.Mapping),
    priority=ConvertPriority.high()
)
def _convert_lookup_mapping(ctx: ConvertCtx) -> Parser:
    ctx.assert_not_query()

    key, value = ctx.typ.__args__
    if key != str:
        ctx.skip()
    return LookupMapping(ctx.update_type(value).convert()
                         ).use_readable_describe(ctx.readable)


@as_converter(lambda x: x.typ == uuid.UUID, priority=ConvertPriority.high())
def _convert_uuid(_: ConvertCtx) -> Parser:
    return RichValue.UUID


@as_converter(
    lambda x: x.typ == datetime.timedelta, priority=ConvertPriority.high()
)
def _convert_timedelta(_: ConvertCtx) -> Parser:
    return RichValue.TimeDelta


@as_converter(
    lambda x: x.typ == DatetimeWithTimezone, priority=ConvertPriority.high()
)
def _convert_datetime(_: ConvertCtx) -> Parser:
    return RichValue.DateTime


@as_converter(
    lambda x: x.typ == datetime.date, priority=ConvertPriority.high()
)
def _convert_date(_: ConvertCtx) -> Parser:
    return RichValue.Date


@as_converter(lambda x: x.typ == t.Any)
def _convert_any_value(_: ConvertCtx) -> Parser:
    return AnyValue


@as_converter(
    lambda x: x.origin == tuple and len(x.typ.__args__) == 2,
    priority=ConvertPriority.high(),
)
def _convert_two_tuple(ctx: ConvertCtx) -> Parser:
    ctx.assert_not_query()
    return TwoTuple(
        ctx.update_type(ctx.typ.__args__[0]).convert(),
        ctx.update_type(ctx.typ.__args__[1]).convert(),
    ).use_readable_describe(ctx.readable)
