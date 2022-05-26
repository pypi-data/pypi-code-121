from fa_purity import (
    Cmd,
    JsonObj,
)
from fa_purity.json.transform import (
    dumps,
)
from fa_singer_io.singer import (
    SingerMessage,
)
from fa_singer_io.singer.record.core import (
    SingerRecord,
)
from fa_singer_io.singer.record.encode import (
    encode_record,
)
from fa_singer_io.singer.schema.core import (
    SingerSchema,
)
from fa_singer_io.singer.schema.encode import (
    encode_schema,
)
from fa_singer_io.singer.state.encode import (
    encode_state,
)
from typing import (
    IO,
)


def encode(singer: SingerMessage) -> JsonObj:
    if isinstance(singer, SingerRecord):
        return encode_record(singer)
    if isinstance(singer, SingerSchema):
        return encode_schema(singer)
    return encode_state(singer)


def emit(target: IO[str], singer: SingerMessage) -> Cmd[None]:
    def _action() -> None:
        target.write(dumps(encode(singer)))
        target.write("\n")

    return Cmd.from_cmd(_action)
