import os
import time
from pprint import pformat
from typing import Any, Dict, Iterable, Set, Tuple

from loguru import logger
from psycopg2.extensions import connection as Conn
from psycopg2.extras import NamedTupleCursor
from tqdm import tqdm
from psycopg2.errors import SerializationFailure, OperationalError

from skit_calls import constants as const
from skit_calls.data.db import connect, postgres
from skit_calls.data.model import Turn


def as_turns(records) -> Iterable[Dict[str, Any]]:
    for record in records:
        yield Turn.from_record(record).to_dict()


def get_query(query_name):
    with open(os.environ[query_name]) as handle:
        return handle.read()


def gen_random_call_ids(
    id_: int,
    start_date: str,
    end_date: str,
    limit: int = const.DEFAULT_CALL_QUANTITY,
    call_type: str = const.INBOUND,
    reported: bool = False,
    use_case: str | None = None,
    lang: str | None = None,
    flow_name: str | None = None,
    min_duration: float | None = None,
    excluded_numbers: Set[str] | None = None,
):
    excluded_numbers = set(excluded_numbers) or set()
    excluded_numbers = excluded_numbers.union(const.DEFAULT_IGNORE_CALLERS_LIST)
    reported_status = 0 if reported else None
    call_filters = {
        const.END_DATE: end_date,
        const.START_DATE: start_date,
        const.ID: id_,
        const.CALL_TYPE: call_type,
        const.RESOLVED: reported_status,
        const.LANG: lang,
        const.EXCLUDED_NUMBERS: tuple(excluded_numbers),
        const.MIN_AUDIO_DURATION: min_duration,
        const.USE_CASE: use_case,
        const.FLOW_NAME: flow_name,
        const.LIMIT: limit + const.MARGIN * limit,
    }

    logger.debug(f"call_filters={pformat(call_filters)} | {limit=}")

    query = get_query(const.RANDOM_CALL_ID_QUERY)

    @postgres()
    def on_connect(conn: Conn):
        with conn.cursor() as cursor:
            cursor.execute(query, call_filters)
            all_ids = cursor.fetchall()
        return tuple(id_[0] for id_ in all_ids)

    return on_connect


def get_call_ids_from_uuids(id_: int, uuids: Tuple[str]) -> Tuple[int]:
    query = get_query(const.CALL_IDS_FROM_UUIDS_QUERY)
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, {const.UUID: uuids, const.ID: id_})
            return tuple(id_[0] for id_ in cursor.fetchall())


def gen_random_calls(
    call_ids: Tuple[int],
    asr_provider: str | None = None,
    states: Set[str] | None = None,
    limit: int = const.TURNS_LIMIT,
    delay: float = const.Q_DELAY,
):
    time.sleep(1)
    query = get_query(const.RANDOM_CALL_DATA_QUERY)
    states = tuple(set(states or [None]))
    turn_filters = {
        const.ASR_PROVIDER: asr_provider,
        const.CONVERSATION_TYPES: (const.UCASE_INPUT,),
        const.CONVERSATION_SUB_TYPES: (const.UCASE_AUDIO,),
        const.STATES: states,
    }
    logger.debug(f"call_filters={pformat(turn_filters)}")

    call_id_size = len(call_ids)
    batch_size = (
        call_id_size // limit
        if call_id_size % limit == 0
        else call_id_size // limit + 1
    )
    logger.debug(f"Creating {batch_size} batches for {call_id_size} calls")
    i = 0

    with tqdm(total=batch_size, desc="Downloading turns for calls dataset.") as pbar:
        while i < call_id_size:
            batch = call_ids[i : i + limit]
            try:
                with connect() as conn:
                    with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
                        cursor.execute(query, {**turn_filters, const.CALL_IDS: batch})
                        result_set = cursor.fetchall()
                        yield from as_turns(result_set)
                        pbar.update(1)
                i += limit
            except (SerializationFailure, OperationalError) as e:
                logger.error(e)
                logger.error(f"This error is common if you are requesting a large dataset. We will retry the batch in a while.")
                time.sleep(delay)
