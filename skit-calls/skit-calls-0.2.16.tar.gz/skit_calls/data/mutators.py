from typing import Union

import pandas as pd

from skit_calls import constants


def get_column_value(df, idx: Union[str, int], column_key: Union[str, int]):
    if idx in df.index:
        return df.loc[idx, column_key]
    else:
        return None


def filter_turns(call_data, conv_key):
    if call_data is not None:
        for i in range(len(call_data)):
            if call_data[i][constants.CONV_UUID] == conv_key:
                return call_data[: i + 1]
    return None


def add_call_history(turns_df: pd.DataFrame) -> pd.DataFrame:

    # group turns into calls and sort turns within calls, into order
    calls_df = (
        turns_df.groupby(constants.CALL_UUID)
        .apply(
            lambda df: df.sort_values(by=constants.CONV_ID, ascending=True).to_dict(
                "records"
            )
        )
        .reset_index()
        .rename(columns={0: constants.CALL_HISTORY})
    )

    # add call data for all turns
    turns_df[constants.CALL_HISTORY] = turns_df[constants.CALL_UUID].apply(
        lambda call_key: get_column_value(
            calls_df.set_index(constants.CALL_UUID),
            idx=call_key,
            column_key=constants.CALL_HISTORY,
        )
    )

    # filter call data to only keep history
    ## assumption here is that turns will be in ascending order of created time
    ## this is enforced by sorting by `conversation id` above
    turns_df[constants.CALL_HISTORY] = turns_df.apply(
        lambda row: filter_turns(row[constants.CALL_HISTORY], row[constants.CONV_UUID]),
        axis=1,
    )

    return turns_df
