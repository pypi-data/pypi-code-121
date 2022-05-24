from typing import Union, List, Optional

from pydantic import BaseModel, Extra, Field, StrictStr, StrictInt, conint, conlist, constr, root_validator, validator


from .record import MAX_LEN_NON_HASHED, MAX_LEN_NON_HASHED_UTILITY_KEYS, SEARCH_KEYS, STRING_KEYS
from .common.custom_types import DateISO8601Field


class Operators(str):
    NOT = "$not"
    GT = "$gt"
    GTE = "$gte"
    LT = "$lt"
    LTE = "$lte"
    OR = "$or"
    LIKE = "$like"


FIND_LIMIT = 100
SEARCH_KEYS_MIN_LEN = 3
SEARCH_KEYS_MAX_LEN = 200

LT_GROUP_EXCEPTION_MESSAGE = f"Incorrect filter. Must contain either {Operators.LT} or {Operators.LTE}, not both"
GT_GROUP_EXCEPTION_MESSAGE = f"Incorrect filter. Must contain either {Operators.GT} or {Operators.GTE}, not both"


NonEmptyStr = constr(strict=True, min_length=1)
NonEmptyStrList = conlist(StrictStr, min_items=1)
NonEmptyIntList = conlist(StrictInt, min_items=1)
NonEmptyDateList = conlist(DateISO8601Field, min_items=1)

Str128 = constr(strict=True, max_length=MAX_LEN_NON_HASHED_UTILITY_KEYS)
Str128List = conlist(Str128, min_items=1)
Str256 = constr(strict=True, max_length=MAX_LEN_NON_HASHED)
Str256List = conlist(Str256, min_items=1)

StrKeyValues = Union[StrictStr, NonEmptyStrList]
Str128Values = Union[Str128, Str128List]
Str256Values = Union[Str256, Str256List]
IntKeyValues = Union[StrictInt, NonEmptyIntList]
DateKeyValues = Union[DateISO8601Field, NonEmptyDateList]


class OperatorsStrFilter(BaseModel):
    not_operator: Optional[StrKeyValues] = Field(alias=Operators.NOT, default=...)

    class Config:
        extra = Extra.forbid


class OperatorsStr128Filter(OperatorsStrFilter):
    not_operator: Optional[Str128Values] = Field(alias=Operators.NOT, default=...)


class OperatorsStr256Filter(OperatorsStrFilter):
    not_operator: Optional[Str256Values] = Field(alias=Operators.NOT, default=...)


class OperatorsStrFilterWithLike(OperatorsStrFilter):
    not_operator: Optional[StrKeyValues] = Field(alias=Operators.NOT, default=None)
    like_operator: StrictStr = Field(alias=Operators.LIKE, default=None)

    @root_validator(pre=True)
    def check_not_empty_filter(cls, values):
        if not values:
            raise ValueError("value is not a valid dict")
        return values

    @validator("like_operator")
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(f"cannot be None")

        return value


class OperatorsStr256FilterWithLike(OperatorsStrFilterWithLike):
    not_operator: Optional[Str256Values] = Field(alias=Operators.NOT, default=None)
    like_operator: StrictStr = Field(alias=Operators.LIKE, default=None)


class OperatorsIntFilter(BaseModel):
    not_operator: Optional[IntKeyValues] = Field(
        alias=Operators.NOT,
    )
    gt_operator: Optional[StrictInt] = Field(
        alias=Operators.GT,
    )
    gte_operator: Optional[StrictInt] = Field(
        alias=Operators.GTE,
    )
    lt_operator: Optional[StrictInt] = Field(
        alias=Operators.LT,
    )
    lte_operator: Optional[StrictInt] = Field(
        alias=Operators.LTE,
    )

    class Config:
        extra = Extra.forbid

    @root_validator(pre=True)
    def check_not_empty_filter(cls, values):
        if not values:
            raise ValueError("value is not a valid dict")
        return values

    @validator("gt_operator", "gte_operator", "lt_operator", "lte_operator")
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(f"cannot be None")

        return value

    @validator("lte_operator")
    def check_lte_conflict(cls, value, values):
        if values.get("lt_operator", None):
            raise ValueError(LT_GROUP_EXCEPTION_MESSAGE)
        return value

    @validator("gte_operator")
    def check_gte_conflict(cls, value, values):
        if values.get("gt_operator", None):
            raise ValueError(GT_GROUP_EXCEPTION_MESSAGE)
        return value


class OperatorsDateFilter(OperatorsIntFilter):
    not_operator: Optional[DateISO8601Field] = Field(
        alias=Operators.NOT,
    )
    gt_operator: Optional[DateISO8601Field] = Field(
        alias=Operators.GT,
    )
    gte_operator: Optional[DateISO8601Field] = Field(
        alias=Operators.GTE,
    )
    lt_operator: Optional[DateISO8601Field] = Field(
        alias=Operators.LT,
    )
    lte_operator: Optional[DateISO8601Field] = Field(
        alias=Operators.LTE,
    )

    class Config:
        extra = Extra.forbid


class OperatorsDateFilterWithoutNotNone(OperatorsDateFilter):
    @validator("not_operator")
    def check_not_none(cls, value):
        if value is None:
            raise ValueError(f"cannot be None")

        return value


StrKey = Union[StrKeyValues, OperatorsStrFilter]
Str128Key = Union[Str128Values, OperatorsStr128Filter]
Str256Key = Union[Str256Values, OperatorsStr256Filter]
StrKeyWithLikeSupport = Union[StrKeyValues, OperatorsStrFilterWithLike]
Str256KeyWithLikeSupport = Union[Str256Values, OperatorsStr256FilterWithLike]
IntKey = Union[IntKeyValues, OperatorsIntFilter]
DateKey = Union[DateKeyValues, OperatorsDateFilter]
DateKeyWithoutNotNone = Union[DateKeyValues, OperatorsDateFilterWithoutNotNone]


class FindFilter(BaseModel):
    limit: conint(ge=1, le=FIND_LIMIT, strict=True) = FIND_LIMIT
    offset: conint(ge=0, strict=True) = 0
    record_key: StrKey = None
    profile_key: StrKey = None
    service_key1: StrKey = None
    service_key2: StrKey = None
    service_key3: StrKey = None
    service_key4: StrKey = None
    service_key5: StrKey = None
    parent_key: StrKey = None
    key1: StrKeyWithLikeSupport = None
    key2: StrKeyWithLikeSupport = None
    key3: StrKeyWithLikeSupport = None
    key4: StrKeyWithLikeSupport = None
    key5: StrKeyWithLikeSupport = None
    key6: StrKeyWithLikeSupport = None
    key7: StrKeyWithLikeSupport = None
    key8: StrKeyWithLikeSupport = None
    key9: StrKeyWithLikeSupport = None
    key10: StrKeyWithLikeSupport = None
    key11: StrKeyWithLikeSupport = None
    key12: StrKeyWithLikeSupport = None
    key13: StrKeyWithLikeSupport = None
    key14: StrKeyWithLikeSupport = None
    key15: StrKeyWithLikeSupport = None
    key16: StrKeyWithLikeSupport = None
    key17: StrKeyWithLikeSupport = None
    key18: StrKeyWithLikeSupport = None
    key19: StrKeyWithLikeSupport = None
    key20: StrKeyWithLikeSupport = None
    search_keys: constr(strict=True, min_length=SEARCH_KEYS_MIN_LEN, max_length=SEARCH_KEYS_MAX_LEN) = None
    range_key1: IntKey = None
    range_key2: IntKey = None
    range_key3: IntKey = None
    range_key4: IntKey = None
    range_key5: IntKey = None
    range_key6: IntKey = None
    range_key7: IntKey = None
    range_key8: IntKey = None
    range_key9: IntKey = None
    range_key10: IntKey = None
    created_at: DateKeyWithoutNotNone = None
    updated_at: DateKeyWithoutNotNone = None
    expires_at: DateKey = None
    version: IntKey = None
    or_operator: Optional[List["FindFilter"]] = Field(alias=Operators.OR)

    @validator("*", pre=True)
    def check_dicts_pre(cls, value):
        if not isinstance(value, dict):
            return value

        if not value:
            raise ValueError("Filter cannot be empty dict")

        return value

    @validator("created_at", "updated_at", pre=True)
    def check_server_dates_not_none(cls, value):
        if value is None:
            raise ValueError(f"cannot be None")

        return value

    @validator("search_keys")
    def check_search_keys_without_regular_keys(cls, value, values):
        non_empty_string_keys = [key for key in values.keys() if values[key] is not None]
        if len(set(SEARCH_KEYS).intersection(set(non_empty_string_keys))) > 0:
            raise ValueError("cannot be used in conjunction with regular key1...key20 lookup")
        return value

    @validator("or_operator")
    def check_or_operator(cls, value, values):
        if values.get("search_keys", None) and len(values["search_keys"]):
            raise ValueError("not compatible with search_keys")
        if len(value) < 2:
            raise ValueError("ensure this value has at least 2 items")
        return value

    @validator("or_operator", each_item=True)
    def check_or_operator_filters(cls, value):
        if not value or not value.__fields_set__:
            raise ValueError("cannot be empty")
        if not value.__fields_set__.issubset(set(STRING_KEYS)):
            raise ValueError(
                f"OR condition supports only filters for fields "
                f"[record_key, profile_key, parent_key, key1...key20, service_key1...service_key5]"
            )
        return value

    @staticmethod
    def getFindLimit():
        return FIND_LIMIT


FindFilter.update_forward_refs()


class FindFilterNonHashed(FindFilter):
    key1: Str256KeyWithLikeSupport = None
    key2: Str256KeyWithLikeSupport = None
    key3: Str256KeyWithLikeSupport = None
    key4: Str256KeyWithLikeSupport = None
    key5: Str256KeyWithLikeSupport = None
    key6: Str256KeyWithLikeSupport = None
    key7: Str256KeyWithLikeSupport = None
    key8: Str256KeyWithLikeSupport = None
    key9: Str256KeyWithLikeSupport = None
    key10: Str256KeyWithLikeSupport = None
    key11: Str256KeyWithLikeSupport = None
    key12: Str256KeyWithLikeSupport = None
    key13: Str256KeyWithLikeSupport = None
    key14: Str256KeyWithLikeSupport = None
    key15: Str256KeyWithLikeSupport = None
    key16: Str256KeyWithLikeSupport = None
    key17: Str256KeyWithLikeSupport = None
    key18: Str256KeyWithLikeSupport = None
    key19: Str256KeyWithLikeSupport = None
    key20: Str256KeyWithLikeSupport = None


class FindFilterRaw(FindFilterNonHashed):
    record_key: Str128Key = None
    profile_key: Str128Key = None
    parent_key: Str128Key = None
    service_key1: Str256Key = None
    service_key2: Str256Key = None
    service_key3: Str256Key = None
    service_key4: Str256Key = None
    service_key5: Str256Key = None
