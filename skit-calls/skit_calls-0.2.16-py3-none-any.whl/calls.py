import csv
import tempfile
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd
from loguru import logger

from skit_calls import constants as const
from skit_calls.data import mutators, query
from skit_calls.data.model import Turn
from skit_calls.utils import optimal_paging_params


def save_turns_in_memory(stream: Iterable[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(list(stream))


def save_turns_on_disk(stream: Iterable[Dict[str, Any]]) -> str:
    _, file_path = tempfile.mkstemp(suffix=const.CSV_FILE)
    with open(file_path, "w", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=Turn.__slots__)
        writer.writeheader()
        for turn in stream:
            writer.writerow(turn)
    return file_path


def sample(
    org_id: str,
    start_date: str,
    end_date: str,
    lang: str,
    call_quantity: int = 200,
    call_type: str = const.INBOUND,
    ignore_callers: List[str] | None = None,
    reported: bool = False,
    use_case: str | None = None,
    flow_name: str | None = None,
    min_duration: float | None = None,
    asr_provider: str | None = None,
    states: List[str] | None = None,
    on_disk: bool = True,
    batch_turns: int = const.TURNS_LIMIT,
    delay: float = const.Q_DELAY,
) -> str | pd.DataFrame:
    """
    Sample calls.

    :param url: The endpoint for fetching call and related data.
    :type url: str

    :param token: An auth token.
    :type token: str

    :param start_date: A start date for the sampling.
    :type start_date: str

    :param end_date: An end date for the sampling.
    :type end_date: str

    :param lang_code: A language code.
    :type lang_code: str

    :param call_quantity: Number of calls to be fetched, defaults to 200
    :type call_quantity: int, optional

    :param call_type: Pick the environment (live or subtesting), defaults to const.LIVE
    :type call_type: str, optional

    :param ignore_callers: A list of callers that should be ignored from sampling, defaults to None
    :type ignore_callers: Optional[List[str]], optional

    :param reported: If True filter only reported calls, defaults to True
    :type reported: bool, optional

    :param resolved: If True filter only resolved calls, defaults to True
    :type resolved: bool, optional

    :param custom_search_key: Custom search filter key, defaults to None
    :type custom_search_key: Optional[str], optional

    :param custom_search_value: Value for custom search filter key, defaults to None
    :type custom_search_value: Optional[str], optional

    :param states: A list of states that should be picked from sampling, defaults to None
    :type ignore_callers: Optional[List[str]], optional

    :param on_disk: "in-memory" (False) vs "files" (True), defaults to None
    :type save: Optional[str], optional

    :return: A directory path if save is set to "files" otherwise path to a file.
    :rtype: str
    """
    random_call_ids = query.gen_random_call_ids(
        org_id,
        start_date,
        end_date,
        limit=call_quantity,
        call_type=call_type,
        lang=lang,
        min_duration=min_duration,
        use_case=use_case,
        flow_name=flow_name,
        excluded_numbers=ignore_callers,
        reported=reported,
    )()
    random_call_data = query.gen_random_calls(
        random_call_ids,
        asr_provider=asr_provider,
        states=states,
        limit=batch_turns,
        delay=delay,
    )
    if on_disk:
        return save_turns_on_disk(random_call_data)
    return save_turns_in_memory(random_call_data)


def select(
    call_ids: Optional[List[int]] = None,
    org_id: Optional[int] = None,
    csv_file: Optional[str] = None,
    uuid_col: Optional[str] = None,
    call_history: bool = False,
    on_disk: bool = True,
    delay: float = const.Q_DELAY
) -> str | pd.DataFrame:
    """
    Sample calls.

    :param call_ids: A list of call ids.
    :type call_ids: List[int]

    :param on_disk: To save "in-memory" (works for <5k calls) vs "files", defaults to True
    :type on_disk: bool

    :return: A directory path if save is set to "files" otherwise path to a file.
    :rtype: str
    """
    try:
        if csv_file and uuid_col and org_id:
            df = pd.read_csv(csv_file)
            call_ids = query.get_call_ids_from_uuids(org_id, tuple(df[uuid_col].unique()))
        else:
            raise ValueError("Both csv_file or uuid_column must be provided.")
        if not call_ids:
            raise ValueError("No call ids or csv file provided.")
        random_call_data = query.gen_random_calls(call_ids, delay=const.Q_DELAY)
        if call_history:
            random_call_data = mutators.add_call_history(random_call_data)
        if on_disk:
            return save_turns_on_disk(random_call_data)
        return save_turns_in_memory(random_call_data)
    except SerializationFailure as e:
        logger.error(e)
        logger.error(f"This error is common if you are requesting a large dataset.")
