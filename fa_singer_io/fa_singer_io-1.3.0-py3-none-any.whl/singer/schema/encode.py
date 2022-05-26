from .core import (
    SingerSchema,
)
from fa_purity import (
    JsonObj,
    JsonValue,
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


def encode_schema(schema: SingerSchema) -> JsonObj:
    bookmark_properties = (
        Maybe.from_optional(schema.bookmark_properties)
        .map(lambda s: freeze([JsonValue(item) for item in s]))
        .to_result()
        .to_union()
    )
    raw_json: Dict[str, UnfoldedJVal] = {
        "type": "SCHEMA",
        "stream": schema.stream,
        "schema": schema.schema.encode(),
        "key_properties": freeze(
            [JsonValue(item) for item in schema.key_properties]
        ),
    }
    if bookmark_properties is not None:
        raw_json["bookmark_properties"] = bookmark_properties
    return from_unfolded_dict(freeze(raw_json))
