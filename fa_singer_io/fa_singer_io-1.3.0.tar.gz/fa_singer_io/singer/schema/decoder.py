from .._utils import (
    all_keys_in,
)
from .core import (
    SingerSchema,
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
from fa_singer_io.json_schema.factory import (
    from_json,
)
from fa_singer_io.singer.errors import (
    MissingKeys,
)


class DecodeError(Exception):
    pass


def build_schema(raw_json: JsonObj) -> ResultE[SingerSchema]:
    required_keys = frozenset({"type", "stream", "schema", "key_properties"})
    check = (
        all_keys_in(frozenset(raw_json), required_keys)
        .alt(lambda m: MissingKeys(m, "raw singer schema"))
        .to_union()
    )
    if check is not None:
        return Result.failure(check)
    parsed_type = Unfolder(raw_json["type"]).to_primitive(str).to_union()
    if parsed_type == "SCHEMA":
        try:
            bookmark_properties = (
                Maybe.from_optional(raw_json.get("bookmark_properties", None))
                .map(Unfolder)
                .map(lambda item: item.to_list_of(str).unwrap())
                .map(lambda item: frozenset(item))
            )
            return SingerSchema.new(
                Unfolder(raw_json["stream"]).to_primitive(str).unwrap(),
                from_json(
                    Unfolder(raw_json["schema"]).to_json().unwrap()
                ).unwrap(),
                frozenset(
                    Unfolder(raw_json["key_properties"])
                    .to_list_of(str)
                    .unwrap()
                ),
                bookmark_properties.value_or(None),
            )
        except UnwrapError as err:
            return Result.failure(err)
    return Result.failure(
        DecodeError(f'Expected "SCHEMA" not "{parsed_type}"')
    )
