from __future__ import (
    annotations,
)

from .._utils import (
    all_keys_in,
)
from dataclasses import (
    dataclass,
)
from fa_purity.json.value.transform import (
    Unfolder,
)
from fa_purity.result import (
    Result,
    ResultE,
)
from fa_singer_io.json_schema.core import (
    JsonSchema,
)
from fa_singer_io.singer.errors import (
    MissingKeys,
)
from typing import (
    FrozenSet,
    Optional,
)


def _check_keys(
    properties: Optional[FrozenSet[str]],
    key_properties: FrozenSet[str],
    bookmark_properties: Optional[FrozenSet[str]],
) -> ResultE[None]:
    if properties is None:
        return (
            Result.failure(
                Exception(
                    "If not properties then not key_properties nor bookmark_properties at SingerSchema"
                )
            )
            if (bool(key_properties) or bool(bookmark_properties))
            else Result.success(None)
        )
    check_keys = all_keys_in(properties, key_properties).alt(
        lambda m: MissingKeys(m, "schema properties")
    )
    check_bookmarks = all_keys_in(properties, bookmark_properties).alt(
        lambda m: MissingKeys(m, "schema properties")
    )
    return check_keys.bind(lambda _: check_bookmarks).alt(Exception)


@dataclass(frozen=True)
class _InnerSingerSchema:
    stream: str
    schema: JsonSchema
    key_properties: FrozenSet[str]
    bookmark_properties: Optional[FrozenSet[str]]


@dataclass(frozen=True)
class SingerSchema(_InnerSingerSchema):
    def __init__(self, obj: _InnerSingerSchema) -> None:
        super().__init__(**obj.__dict__)  # type: ignore[misc]

    @classmethod
    def new(
        cls,
        stream: str,
        schema: JsonSchema,
        key_properties: FrozenSet[str],
        bookmark_properties: Optional[FrozenSet[str]],
    ) -> ResultE[SingerSchema]:
        raw = schema.encode()
        props = raw.get("properties", None)
        properties = (
            frozenset(Unfolder(props).to_json().unwrap())
            if props is not None
            else None
        )
        return _check_keys(
            properties, key_properties, bookmark_properties
        ).map(
            lambda _: SingerSchema(
                _InnerSingerSchema(
                    stream, schema, key_properties, bookmark_properties
                )
            )
        )
