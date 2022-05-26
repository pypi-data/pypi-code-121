from .._utils import (
    all_keys_in,
)
from .core import (
    SingerRecord,
)
from fa_purity import (
    JsonObj,
    Maybe,
    Result,
    ResultE,
)
from fa_purity.json.value.transform import (
    Unfolder,
)
from fa_purity.result import (
    UnwrapError,
)
from fa_singer_io.singer.errors import (
    MissingKeys,
)
from fa_singer_io.time import (
    DateTime,
)
from typing import (
    TypeVar,
)

_T = TypeVar("_T")


def build_record(raw_json: JsonObj) -> ResultE[SingerRecord]:
    required_keys = frozenset({"type", "stream", "record"})
    check = (
        all_keys_in(frozenset(raw_json), required_keys)
        .alt(lambda m: MissingKeys(m, "raw singer record"))
        .to_union()
    )
    if check is not None:
        return Result.failure(check)
    try:
        parsed_type = Unfolder(raw_json["type"]).to_primitive(str).unwrap()
        time_extracted = (
            Maybe.from_optional(raw_json.get("time_extracted", None))
            .map(Unfolder)
            .map(lambda i: i.to_primitive(str).unwrap())
            .map(DateTime.parse)
        )
        if parsed_type == "RECORD":
            record = SingerRecord(
                Unfolder(raw_json["stream"]).to_primitive(str).unwrap(),
                Unfolder(raw_json["record"]).to_json().unwrap(),
                time_extracted.value_or(None),
            )
            return Result.success(record)
    except UnwrapError[_T, Exception] as err:
        return Result.failure(err.container.unwrap_fail())
    return Result.failure(Exception(f'Expected "RECORD" not "{parsed_type}"'))
