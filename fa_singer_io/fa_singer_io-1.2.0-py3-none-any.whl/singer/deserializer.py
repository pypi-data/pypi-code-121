from dataclasses import (
    dataclass,
)
from fa_purity import (
    Cmd,
    JsonObj,
    PureIter,
    Result,
    ResultE,
)
from fa_purity.json.factory import (
    loads,
)
from fa_purity.json.value.transform import (
    Unfolder,
)
from fa_purity.pure_iter.factory import (
    unsafe_from_cmd,
)
from fa_purity.pure_iter.transform import (
    filter_opt,
)
from fa_purity.union import (
    inl,
)
from fa_singer_io.singer import (
    SingerMessage,
)
from fa_singer_io.singer.errors import (
    MissingKeys,
)
from fa_singer_io.singer.record.decoder import (
    build_record,
)
from fa_singer_io.singer.schema.decoder import (
    build_schema,
)
from fa_singer_io.singer.state.decoder import (
    build_state,
)
from typing import (
    IO,
    Iterable,
)


@dataclass(frozen=True)
class _TmpWrapper:
    value: SingerMessage


def deserialize(raw: JsonObj) -> ResultE[SingerMessage]:
    parsed_type = (
        Unfolder(raw["type"])
        .to_primitive(str)
        .alt(lambda _: MissingKeys(frozenset(["type"]), "raw singer msg"))
    )
    _parsed_type = parsed_type.to_union()
    if _parsed_type == "RECORD":
        return build_record(raw).map(inl)
    if _parsed_type == "SCHEMA":
        return build_schema(raw).map(inl)
    if _parsed_type == "STATE":
        return build_state(raw).map(inl)
    return Result.failure(
        parsed_type.map(lambda t: Exception(f"Unknown type '{t}'"))
        .alt(Exception)
        .to_union()
    )


def _read_file(file: IO[str]) -> PureIter[str]:
    # IO file is supposed to be read-only
    def _iter_lines() -> Iterable[str]:
        line = file.readline()
        while line:
            yield line
            line = file.readline()

    return unsafe_from_cmd(Cmd.from_cmd(lambda: iter(_iter_lines())))


def try_from_file(file: IO[str]) -> PureIter[ResultE[SingerMessage]]:
    return (
        _read_file(file)
        .map(loads)
        .map(lambda r: r.alt(Exception).bind(deserialize))
    )


def from_file(file: IO[str]) -> PureIter[SingerMessage]:
    return try_from_file(file).map(lambda r: r.unwrap())


def from_file_ignore_failed(file: IO[str]) -> PureIter[SingerMessage]:
    return (
        try_from_file(file)
        .map(lambda r: r.map(_TmpWrapper).value_or(None))
        .transform(lambda i: filter_opt(i))
        .map(lambda w: w.value)
    )
