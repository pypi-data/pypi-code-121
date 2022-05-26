from .core import (
    SingerRecord,
)
from fa_purity import (
    JsonObj,
    Maybe,
    UnfoldedJVal,
)
from fa_purity.frozen import (
    freeze,
)
from fa_purity.json.factory import (
    from_unfolded_dict,
)
from typing import (
    Dict,
)


def encode_record(record: SingerRecord) -> JsonObj:
    time_str = Maybe.from_optional(record.time_extracted).map(
        lambda date: date.to_utc_str()
    )
    raw_json: Dict[str, UnfoldedJVal] = {
        "type": "RECORD",
        "stream": record.stream,
        "record": record.record,
    }
    if time_str.map(bool).value_or(False):
        raw_json["time_extracted"] = time_str.unwrap()

    return from_unfolded_dict(freeze(raw_json))
