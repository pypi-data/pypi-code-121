from datetime import datetime, timezone
from enum import Enum
from itertools import chain
from typing import List
# create logger
from bigeye_sdk.log import get_logger

log = get_logger(__file__)


def int_enum_enum_list_joined(enum: Enum.__class__, delimiter: str = '\n') -> str:
    return delimiter.join([f'{t.name}:{t.value}' for t in enum])


def merge_list_of_lists(l: List[list]):
    for i in l:
        for si in i:
            yield si


def split_list_n_chunks(l: list, n: int) -> list:
    for i in range(0, len(l), n):
        yield l[i:i + n]


def split_list_in_half(l: list) -> List[List[dict]]:
    middle_ix = len(l) // 2

    data_first_500 = l[:middle_ix]
    data_remainder = l[middle_ix:]

    return [data_first_500, data_remainder]


def dynamic_clz_import(fqc):
    fqc_split = fqc.split('.')
    clz_name = fqc_split.pop()
    module = '.'.join(fqc_split)
    mod = __import__(module, fromlist=[clz_name])
    return getattr(mod, clz_name)


def date_time_2_string(dt: datetime, include_tz_offset: bool = True) -> str:
    if include_tz_offset:
        return dt.astimezone(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        return datetime.isoformat()


def remove_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def chain_lists(ll: List[list]) -> List:
    return list(chain.from_iterable(ll))
