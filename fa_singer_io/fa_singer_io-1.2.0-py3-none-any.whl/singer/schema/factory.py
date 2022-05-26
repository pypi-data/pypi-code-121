from .core import (
    SingerSchema,
)
from fa_singer_io.json_schema.core import (
    JsonSchema,
)


def from_jschema(
    stream: str,
    schema: JsonSchema,
) -> SingerSchema:
    return SingerSchema.new(stream, schema, frozenset([]), None).unwrap()
