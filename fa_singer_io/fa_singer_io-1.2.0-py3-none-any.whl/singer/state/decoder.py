from .._utils import (
    all_keys_in,
)
from .core import (
    SingerState,
)
from fa_purity.json.factory import (
    JsonObj,
)
from fa_purity.json.value.transform import (
    Unfolder,
)
from fa_purity.result import (
    Result,
    ResultE,
    UnwrapError,
)
from fa_singer_io.singer.errors import (
    MissingKeys,
)
from typing import (
    TypeVar,
)

_T = TypeVar("_T")


def build_state(raw_json: JsonObj) -> ResultE[SingerState]:
    required_keys = frozenset({"type", "value"})
    check = (
        all_keys_in(frozenset(raw_json), required_keys)
        .alt(lambda m: MissingKeys(m, "raw singer state"))
        .to_union()
    )
    if check is not None:
        return Result.failure(check)
    try:
        parsed_type = Unfolder(raw_json["type"]).to_primitive(str).unwrap()
        if parsed_type == "STATE":
            record = SingerState(
                Unfolder(raw_json["value"]).to_json().unwrap(),
            )
            return Result.success(record)
    except UnwrapError[_T, Exception] as err:
        return Result.failure(err.container.unwrap_fail())
    return Result.failure(Exception(f'Expected "RECORD" not "{parsed_type}"'))
