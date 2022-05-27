from typing import (Optional, List, Dict, SupportsInt, SupportsFloat, Any,
                    Callable, TypeVar, Container, Tuple, Sequence, Type, Union)
from bson.objectid import ObjectId

from ..dt.utils import *
from ..error.utils import InputDataError
from ..safetext import converter
from ..data.nametuple import is_named_tuple


_escape = converter.to_safe_html
_assert_error_type = AssertionError
_ensure_error_type = InputDataError


In_T = TypeVar('In_T')
Formatted_T = TypeVar('Formatted_T')
Out_T = TypeVar('Out_T')

Dict_In_T = Union[In_T, Dict[str, In_T]]
Optional_Dict_In_T = Union[In_T, Dict[str, Optional[In_T]], None]

Checker_T = Callable
Checker_Union = Union[Checker_T, Optional[Tuple]]


def _get_scalar(name: str, value: Optional_Dict_In_T) -> Optional[In_T]:
    return value.get(name) if isinstance(value, dict) else value


def _raise_required_error(name: str, error_type: type):
    raise error_type(f"{_escape(name)} not provided!")


def _extract_checker(checker_union: Checker_Union) \
        -> Tuple[Checker_T, Sequence]:
    if isinstance(checker_union, (tuple, list)):
        if not callable(checker_union[0]):
            raise TypeError(f"Invalid checker: {checker_union[0]}")
        checker_func = checker_union[0]
        checker_args = checker_union[1:]
    elif callable(checker_union):
        checker_func = checker_union
        checker_args = []
    else:
        raise TypeError(f"Invalid checker: {checker_union}")
    return checker_func, checker_args


def _ensure(name: str,
            value: Optional_Dict_In_T,
            required: bool,
            default_to: Optional[In_T],
            strict_none: bool,
            formatter: Optional[Callable[[str, In_T], Formatted_T]],
            checker: Checker_Union,
            error_type: type) -> Optional[Out_T]:
    in_value = _get_scalar(name, value)
    if strict_none and in_value is None or not strict_none and not in_value \
            and in_value != 0:
        if required:
            _raise_required_error(name, error_type)
        else:
            return default_to
    if formatter:
        if not callable(formatter):
            raise error_type(f"Invalid formatter: {formatter}!")
        formatted_value = formatter(name, in_value)
    else:
        formatted_value = in_value

    if checker:
        checker_func, checker_args = _extract_checker(checker)
        converted_value = checker_func(name, formatted_value, error_type,
                                       *checker_args)
    else:
        converted_value = formatted_value
    return converted_value


def ensure_not_none(name: str, value: Dict_In_T) -> Out_T:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=None, error_type=_ensure_error_type)


def assert_not_none(name: str, value: Dict_In_T) -> Out_T:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=None, error_type=_assert_error_type)


# noinspection PyUnusedLocal
def ensure_str(name: str, value, default_to: Optional[str] = None) \
        -> Optional[str]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=lambda n, v, e: str(v),
                   error_type=_ensure_error_type)


def ensure_str_legacy(value, default_to: Optional[str] = None) -> Optional[str]:
    from warnings import warn
    warn("ensure_str_legacy is deprecated. Please use ensure_str instead.",
         DeprecationWarning, stacklevel=2)
    return default_to if value is None else str(value)


def ensure_not_none_str(name: str, value) -> str:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=lambda n, v: str(v), checker=None,
                   error_type=_ensure_error_type)


def assert_not_none_str(name: str, value) -> str:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=lambda n, v: str(v), checker=None,
                   error_type=_assert_error_type)


In_Bool = Any
Out_Bool = int
Dict_In_Bool = Union[In_Bool, Dict[str, In_Bool]]
Optional_Dict_In_Bool = Union[In_Bool, Dict[str, Optional[In_Bool]], None]


def _check_bool(name: str, value: In_Bool, error_type: type) -> Out_Bool:
    try:
        if isinstance(value, str):
            return value.lower() not in ('false', 'no', '0')
        else:
            return bool(value)
    except (TypeError, ValueError):
        raise error_type(f"Invalid {_escape(name)}: {_escape(value)}")


def ensure_bool_legacy(value, default_to: Optional[bool] = None) \
        -> Optional[bool]:
    return default_to if value is None else bool(value)


def ensure_bool(name: str, value, default_to: Optional[bool] = None) \
        -> Optional[bool]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=_check_bool,
                   error_type=_ensure_error_type)


def assert_bool(name: str, value, default_to: Optional[bool] = None) \
        -> Optional[bool]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=_check_bool,
                   error_type=_assert_error_type)


def ensure_not_none_bool(name: str, value) -> bool:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=_check_bool,
                   error_type=_ensure_error_type)


def assert_not_none_bool(name: str, value) -> bool:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=_check_bool,
                   error_type=_assert_error_type)


In_Int = Union[str, SupportsInt]
Out_Int = int
Dict_In_Int = Union[In_Int, Dict[str, In_Int]]
Optional_Dict_In_Int = Union[In_Int, Dict[str, Optional[In_Int]], None]


def _check_int(name: str, value: In_Int, error_type: type) -> Out_Int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise error_type(f"Invalid {_escape(name)}: {_escape(value)}")


def ensure_int(name: str, value: Optional_Dict_In_Int,
               default_to: Optional[int] = None) -> Optional[Out_Int]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=_check_int,
                   error_type=_ensure_error_type)


def assert_int(name: str, value: Optional_Dict_In_Int,
               default_to: Optional[int] = None) -> Optional[Out_Int]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=_check_int,
                   error_type=_assert_error_type)


def ensure_not_none_int(name: str, value: Dict_In_Int) -> Out_Int:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=_check_int,
                   error_type=_ensure_error_type)


def assert_not_none_int(name: str, value: Dict_In_Int) -> Out_Int:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=_check_int,
                   error_type=_assert_error_type)


In_Float = Union[str, SupportsFloat]
Out_Float = float
Dict_In_Float = Union[In_Float, Dict[str, In_Float]]
Optional_Dict_In_Float = Union[In_Float, Dict[str, Optional[In_Float]], None]


def _check_float(name: str, value: In_Float, error_type: type) -> Out_Float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise error_type(f"Invalid {_escape(name)}: {_escape(value)}")


def ensure_float(name: str, value: Optional_Dict_In_Float,
                 default_to: Optional[float] = None) -> Optional[Out_Float]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=_check_float,
                   error_type=_ensure_error_type)


def assert_float(name: str, value: Optional_Dict_In_Float,
                 default_to: Optional[float] = None) -> Optional[Out_Float]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=_check_float,
                   error_type=_assert_error_type)


def ensure_not_none_float(name: str, value: Dict_In_Float) -> Out_Float:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=_check_float,
                   error_type=_ensure_error_type)


def assert_not_none_float(name: str, value: Dict_In_Float) -> Out_Float:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=_check_float,
                   error_type=_assert_error_type)


In_ObjId = Union[str, ObjectId]
Out_ObjId = ObjectId
Dict_In_ObjId = Union[In_ObjId, Dict[str, In_ObjId]]
Optional_Dict_In_ObjId = Union[In_ObjId, Dict[str, Optional[In_ObjId]], None]


def _check_objid(name: str, value: In_ObjId, error_type: type) -> ObjectId:
    if isinstance(value, ObjectId):
        return value
    value_str = str(value)
    if not ObjectId.is_valid(value_str):
        raise error_type(
            f"{_escape(name)} is not a valid object id: {_escape(value)}")
    return ObjectId(value_str)


def ensure_objid(name: str, value: Optional_Dict_In_ObjId,
                 default_to: Optional[ObjectId] = None) -> Optional[ObjectId]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=_check_objid,
                   error_type=_ensure_error_type)


def assert_objid(name: str, value: Optional_Dict_In_ObjId,
                 default_to: Optional[ObjectId] = None) -> Optional[ObjectId]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=_check_objid,
                   error_type=_assert_error_type)


def ensure_not_none_objid(name: str, value: Dict_In_ObjId) -> ObjectId:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=_check_objid,
                   error_type=_ensure_error_type)


def assert_not_none_objid(name: str, value: Dict_In_ObjId) -> ObjectId:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=_check_objid,
                   error_type=_assert_error_type)


def _check_objid_str(name: str, value: In_ObjId, error_type: type) -> str:
    return str(_check_objid(name, value, error_type))


def ensure_objid_str(name: str, value: Optional_Dict_In_ObjId,
                     default_to: Optional[str] = None) -> Optional[str]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=_check_objid_str,
                   error_type=_ensure_error_type)


def assert_objid_str(name: str, value: Optional_Dict_In_ObjId,
                     default_to: Optional[str] = None) -> Optional[str]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=_check_objid_str,
                   error_type=_assert_error_type)


def ensure_not_none_objid_str(name: str, value: Dict_In_ObjId) -> str:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=_check_objid_str,
                   error_type=_ensure_error_type)


def assert_not_none_objid_str(name: str, value: Dict_In_ObjId) -> str:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=_check_objid_str,
                   error_type=_assert_error_type)


Enum_T = TypeVar('Enum_T')
In_Enum = Union[str, Enum_T]
Out_Enum = Enum_T
Dict_In_Enum = Union[In_Enum, Dict[str, In_Enum]]
Optional_Dict_In_Enum = Union[In_Enum, Dict[str, Optional[In_Enum]], None]


def _check_enum(name: str, value: Dict_In_Enum, error_type: type,
                enum_type: Type[Enum_T]) -> Enum_T:
    try:
        out_value = enum_type(value)
    except ValueError:
        raise error_type(
            f"{_escape(name)} is not a valid {_escape(enum_type.__name__)} "
            f"enum: {_escape(value)}")
    return out_value


def ensure_enum(name: str, value: Dict_In_Enum, enum_type: Type[Enum_T],
                default_to: Optional[Enum_T] = None) -> Optional[Enum_T]:
    """
    Ensure input is an enum of given type
    :param name: Name of the value
    :param value: The value of a dict containing the value keyed by `name`.
    :param enum_type: The expected enum type.
    :param default_to: The default value.
    :return: The value converted into `enum_type`.
    """
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=(_check_enum, enum_type),
                   error_type=_ensure_error_type)


def assert_enum(name: str, value: Dict_In_Enum, enum_type: Type[Enum_T],
                default_to: Optional[Enum_T] = None) -> Optional[Enum_T]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=(_check_enum, enum_type),
                   error_type=_assert_error_type)


def ensure_not_none_enum(name: str, value: Optional_Dict_In_Enum,
                         enum_type: Type[Enum_T]) -> Enum_T:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=(_check_enum, enum_type),
                   error_type=_ensure_error_type)


def assert_not_none_enum(name: str, value: Optional_Dict_In_Enum,
                         enum_type: Type[Enum_T]) -> Enum_T:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=(_check_enum, enum_type),
                   error_type=_assert_error_type)


In_DT = Union[str, datetime]
Optional_In_DT = Union[str, datetime, None]
Out_DT = datetime
Dict_In_DT = Union[In_DT, Dict[str, In_DT]]
Optional_Dict_In_DT = Union[In_DT, Dict[str, Optional[In_DT]], None]


def _check_datetime(name: str, value: In_DT, error_type: type,
                    fmt: str) -> datetime:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(value, fmt)
    except (TypeError, ValueError):
        raise error_type(
            f"Invalid {_escape(name)} text {_escape(value)} on format "
            f"{_escape(fmt)}")


def ensure_datetime(name: str, value: Optional_Dict_In_DT,
                    fmt: str = DATETIME_FMT_FULL,
                    default_to: Optional[datetime] = None) \
        -> Optional[datetime]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=(_check_datetime, fmt),
                   error_type=_ensure_error_type)


def assert_datetime(name: str, value: Optional_Dict_In_DT,
                    fmt: str = DATETIME_FMT_FULL,
                    default_to: Optional[datetime] = None) \
        -> Optional[datetime]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=(_check_datetime, fmt),
                   error_type=_assert_error_type)


def ensure_not_none_datetime(name: str, value: Dict_In_DT,
                             fmt: str = DATETIME_FMT_FULL) -> datetime:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=(_check_datetime, fmt),
                   error_type=_ensure_error_type)


def assert_not_none_datetime(name: str, value: Dict_In_DT,
                             fmt: str = DATETIME_FMT_FULL) -> datetime:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=(_check_datetime, fmt),
                   error_type=_assert_error_type)


def _check_datetime_str(name: str, value: In_DT, error_type: type,
                        fmt: str) -> str:
    return _check_datetime(name, value, error_type, fmt).strftime(fmt)


def ensure_datetime_str(name: str, value: Optional_Dict_In_DT,
                        fmt: str = DATETIME_FMT_FULL,
                        default_to: Optional[str] = None) -> Optional[str]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=(_check_datetime_str, fmt),
                   error_type=_ensure_error_type)


def assert_datetime_str(name: str, value: Optional_Dict_In_DT,
                        fmt: str = DATETIME_FMT_FULL,
                        default_to: Optional[str] = None) -> Optional[str]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=(_check_datetime_str, fmt),
                   error_type=_assert_error_type)


def ensure_not_none_datetime_str(name: str, value: Dict_In_DT,
                                 fmt: str = DATETIME_FMT_FULL) -> str:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=(_check_datetime_str, fmt),
                   error_type=_ensure_error_type)


def assert_not_none_datetime_str(name: str, value: Dict_In_DT,
                                 fmt: str = DATETIME_FMT_FULL) -> str:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=(_check_datetime_str, fmt),
                   error_type=_assert_error_type)


In_Sequence = Union[str, Sequence]
Dict_In_Sequence = Union[In_Sequence, Dict[str, In_Sequence]]
Optional_Dict_In_Sequence = Union[
    In_Sequence, Dict[str, Optional[In_Sequence]], None]
Out_Sequence = Tuple[Out_T, ...]
Out_List = List[Out_T]
Out_Tuple = Tuple[Out_T, ...]

Sequence_Formatter = Callable  # [[str, In_List], Formatted_List]

Item_Checker = Callable  # [[str, In_T], Out_T]
Item_Checker_Union = Union[Item_Checker, Optional[Tuple], None]


def str_splitter(sep: str = ',', strip: bool = True,
                 drop_empty: bool = True) -> Sequence_Formatter:
    def to_list_formatter(_: str, value: In_Sequence) -> Sequence:
        if isinstance(value, (list, tuple)):
            return list(value)
        str_list = str(value).split(sep)
        if strip:
            str_list = [s.strip() for s in str_list]
        if drop_empty:
            str_list = [s for s in str_list if s]
        return str_list

    return to_list_formatter


def _check_seq(name: str, value: Sequence, error_type: type,
               allowed_types: Optional[Tuple[type, ...]],
               target_types: Optional[Tuple[type, ...]],
               item_checker: Item_Checker_Union = None) -> Sequence:
    if is_named_tuple(value):
        raise error_type(
            f"{_escape(name)} is a NamedTuple, but {allowed_types} is "
            f"expected!")
    if not allowed_types:
        allowed_types = (list, tuple, set)
    if not target_types:
        target_types = (list, tuple, set)
    if not isinstance(value, allowed_types):
        raise error_type(
            f"{_escape(name)} is not valid {allowed_types}: {_escape(value)}")

    if not item_checker:
        if isinstance(value, target_types):
            return value
        else:
            return target_types[0](value)

    item_checker_func, item_checker_args = _extract_checker(item_checker)
    converted = (item_checker_func(f"{name}[{i}]", item, *item_checker_args) for
                 i, item in enumerate(value))
    if isinstance(value, target_types):
        # noinspection PyArgumentList
        converted = type(value)(converted)
    else:
        converted = target_types[0](converted)
    return converted


def ensure_list(name: str, value: Optional_Dict_In_Sequence,
                formatter: Sequence_Formatter = None,
                allow_empty_list: bool = True,
                default_to: Optional[Out_List] = None) -> Optional[Out_List]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=allow_empty_list,
                   formatter=formatter, checker=(_check_seq, None, (list,)),
                   error_type=_ensure_error_type)


def assert_list(name: str, value: Optional_Dict_In_Sequence,
                formatter: Sequence_Formatter = None,
                allow_empty_list: bool = True,
                default_to: Optional[Out_List] = None) -> Optional[Out_List]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=allow_empty_list,
                   formatter=formatter, checker=(_check_seq, None, (list,)),
                   error_type=_assert_error_type)


def ensure_not_none_list(name: str, value: Dict_In_Sequence,
                         formatter: Sequence_Formatter = None,
                         allow_empty_list: bool = True) -> Out_List:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=allow_empty_list,
                   formatter=formatter, checker=(_check_seq, None, (list,)),
                   error_type=_ensure_error_type)


def assert_not_none_list(name: str, value: Dict_In_Sequence,
                         formatter: Sequence_Formatter = None,
                         allow_empty_list: bool = True) -> Out_List:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=allow_empty_list,
                   formatter=formatter, checker=(_check_seq, None, (list,)),
                   error_type=_assert_error_type)


def ensure_list_of(name: str, value: Optional_Dict_In_Sequence,
                   item_checker: Item_Checker_Union,
                   formatter: Sequence_Formatter = None,
                   allow_empty_list: bool = True,
                   default_to: Optional[Out_List] = None) -> Optional[Out_List]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=allow_empty_list,
                   formatter=formatter,
                   checker=(_check_seq, None, (list,), item_checker),
                   error_type=_ensure_error_type)


def assert_list_of(name: str, value: Optional_Dict_In_Sequence,
                   item_checker: Item_Checker_Union,
                   formatter: Sequence_Formatter = None,
                   allow_empty_list: bool = True,
                   default_to: Optional[Out_List] = None) -> Optional[Out_List]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=allow_empty_list,
                   formatter=formatter,
                   checker=(_check_seq, None, (list,), item_checker),
                   error_type=_assert_error_type)


def ensure_not_none_list_of(name: str, value: Dict_In_Sequence,
                            item_checker: Item_Checker_Union,
                            formatter: Sequence_Formatter = None,
                            allow_empty_list: bool = True) -> Out_List:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=allow_empty_list,
                   formatter=formatter,
                   checker=(_check_seq, None, (list,), item_checker),
                   error_type=_ensure_error_type)


def assert_not_none_list_of(name: str, value: Dict_In_Sequence,
                            item_checker: Item_Checker_Union,
                            formatter: Sequence_Formatter = None,
                            allow_empty_list: bool = True) -> Out_List:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=allow_empty_list,
                   formatter=formatter,
                   checker=(_check_seq, None, (list,), item_checker),
                   error_type=_assert_error_type)


def ensure_tuple(name: str, value: Optional_Dict_In_Sequence,
                 formatter: Sequence_Formatter = None,
                 allow_empty_tuple: bool = True,
                 default_to: Optional[Out_Tuple] = None) -> Optional[Out_Tuple]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=allow_empty_tuple,
                   formatter=formatter, checker=(_check_seq, None, (tuple,)),
                   error_type=_ensure_error_type)


def assert_tuple(name: str, value: Optional_Dict_In_Sequence,
                 formatter: Sequence_Formatter = None,
                 allow_empty_tuple: bool = True,
                 default_to: Optional[Out_Tuple] = None) -> Optional[Out_Tuple]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=allow_empty_tuple,
                   formatter=formatter, checker=(_check_seq, None, (tuple,)),
                   error_type=_assert_error_type)


def ensure_not_none_tuple(name: str, value: Dict_In_Sequence,
                          formatter: Sequence_Formatter = None,
                          allow_empty_tuple: bool = True) -> Out_Tuple:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=allow_empty_tuple,
                   formatter=formatter, checker=(_check_seq, None, (tuple,)),
                   error_type=_ensure_error_type)


def assert_not_none_tuple(name: str, value: Dict_In_Sequence,
                          formatter: Sequence_Formatter = None,
                          allow_empty_tuple: bool = True) -> Out_Tuple:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=allow_empty_tuple,
                   formatter=formatter, checker=(_check_seq, None, (tuple,)),
                   error_type=_assert_error_type)


def ensure_tuple_of(name: str, value: Optional_Dict_In_Sequence,
                    item_checker: Item_Checker_Union,
                    formatter: Sequence_Formatter = None,
                    allow_empty_tuple: bool = True,
                    default_to: Optional[Out_Tuple] = None) \
        -> Optional[Out_Tuple]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=allow_empty_tuple,
                   formatter=formatter,
                   checker=(_check_seq, None, (tuple,), item_checker),
                   error_type=_ensure_error_type)


def assert_tuple_of(name: str, value: Optional_Dict_In_Sequence,
                    item_checker: Item_Checker_Union,
                    formatter: Sequence_Formatter = None,
                    allow_empty_tuple: bool = True,
                    default_to: Optional[Out_Tuple] = None) \
        -> Optional[Out_Tuple]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=allow_empty_tuple,
                   formatter=formatter,
                   checker=(_check_seq, None, (tuple,), item_checker),
                   error_type=_assert_error_type)


def ensure_not_none_tuple_of(name: str, value: Dict_In_Sequence,
                             item_checker: Item_Checker_Union,
                             formatter: Sequence_Formatter = None,
                             allow_empty_tuple: bool = True) -> Out_Tuple:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=allow_empty_tuple,
                   formatter=formatter,
                   checker=(_check_seq, None, (tuple,), item_checker),
                   error_type=_ensure_error_type)


def assert_not_none_tuple_of(name: str, value: Dict_In_Sequence,
                             item_checker: Item_Checker_Union,
                             formatter: Sequence_Formatter = None,
                             allow_empty_tuple: bool = True) -> Out_Tuple:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=allow_empty_tuple,
                   formatter=formatter,
                   checker=(_check_seq, None, (tuple,), item_checker),
                   error_type=_assert_error_type)


def _check_in(name: str, value: In_T, error_type: type,
              allowed_values: Container[In_T]) -> In_T:
    if value not in allowed_values:
        raise error_type(f"{_escape(name)} is not valid: {_escape(value)}.")
    return value


def ensure_in(name: str, value: Optional_Dict_In_T,
              allowed_values: Container[In_T],
              default_to: Optional[In_T] = None) -> Optional[In_T]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=(_check_in, allowed_values),
                   error_type=_ensure_error_type)


def assert_in(name: str, value: Optional_Dict_In_T,
              allowed_values: Container[In_T],
              default_to: Optional[In_T] = None) -> Optional[In_T]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=False,
                   formatter=None, checker=(_check_in, allowed_values),
                   error_type=_assert_error_type)


def ensure_not_none_in(name: str, value: Optional_Dict_In_T,
                       allowed_values: Container[In_T]) -> In_T:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=(_check_in, allowed_values),
                   error_type=_ensure_error_type)


def assert_not_none_in(name: str, value: Optional_Dict_In_T,
                       allowed_values: Container[In_T]) -> In_T:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=False,
                   formatter=None, checker=(_check_in, allowed_values),
                   error_type=_assert_error_type)


Allowed_Types = Union[type, Tuple[type, ...], List[type]]


def _check_type(name: str, value: In_T, error_type: type,
                allowed_types: Allowed_Types) -> In_T:
    try:
        if isinstance(allowed_types, list):
            for allowed_type in allowed_types:
                if isinstance(value, allowed_type):
                    return value
        else:
            if isinstance(value, allowed_types):
                return value
            elif isinstance(value, str):
                if allowed_types is int:
                    return _check_int(name, value, error_type)
                elif allowed_types is bool:
                    return _check_bool(name, value, error_type)
                elif allowed_types is float:
                    return _check_float(name, value, error_type)
                elif allowed_types is datetime:
                    return _check_datetime(name, value, error_type)
        raise error_type(f"{_escape(name)} is not valid {allowed_types}: {value}.")
    except TypeError:
        raise error_type(f"allowed_types is not a valid type or tuple of types: {allowed_types}")
    return value


def from_union_to_types(union) -> Tuple[Type, ...]:
    args = getattr(union, '__args__', None)
    if args is not None:
        return args
    raise NotImplementedError(f"Cannot types from union {union}.")


def ensure_of(name: str, value: Optional_Dict_In_T,
              allowed_types: Allowed_Types,
              default_to: Optional[In_T] = None) -> Optional[In_T]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=(_check_type, allowed_types),
                   error_type=_ensure_error_type)


def assert_of(name: str, value: Optional_Dict_In_T,
              allowed_types: Allowed_Types,
              default_to: Optional[In_T] = None) -> Optional[In_T]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=(_check_type, allowed_types),
                   error_type=_assert_error_type)


def ensure_not_none_of(name: str, value: Dict_In_T,
                       allowed_types: Allowed_Types) -> In_T:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=(_check_type, allowed_types),
                   error_type=_ensure_error_type)


def assert_not_none_of(name: str, value: Dict_In_T,
                       allowed_types: Allowed_Types) -> In_T:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=(_check_type, allowed_types),
                   error_type=_assert_error_type)


Dict_In_Callable = Union[Callable, Dict[str, Callable]]
Optional_Dict_In_Callable = Union[Callable, Dict[str, Optional[Callable]], None]


def _check_callable(name: str, value: Callable, error_type: type):
    if not callable(value):
        raise error_type(f"{_escape(name)} is not callable: {_escape(value)}")
    return value


def ensure_callable(name: str, value: Optional_Dict_In_Callable,
                    default_to: Optional[Callable] = None) \
        -> Optional[Callable]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=_check_callable,
                   error_type=_ensure_error_type)


def assert_callable(name: str, value: Optional_Dict_In_Callable,
                    default_to: Optional[Callable] = None) \
        -> Optional[Callable]:
    return _ensure(name, value, required=False, default_to=default_to,
                   strict_none=True,
                   formatter=None, checker=_check_callable,
                   error_type=_assert_error_type)


def ensure_not_none_callable(name: str, value: Dict_In_Callable) -> Callable:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=_check_callable,
                   error_type=_ensure_error_type)


def assert_not_none_callable(name: str, value: Dict_In_Callable) -> Callable:
    return _ensure(name, value, required=True, default_to=None,
                   strict_none=True,
                   formatter=None, checker=_check_callable,
                   error_type=_assert_error_type)
