from fa_purity import (
    ResultE,
)
from fa_singer_io.singer.record.core import (
    SingerRecord,
)
from fa_singer_io.singer.schema.core import (
    SingerSchema,
)


def validate_record(
    schema: SingerSchema, record: SingerRecord
) -> ResultE[None]:
    return schema.schema.validate(record.record).alt(Exception)
