################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2021, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

from typing import Dict, Tuple, Union, List, Optional
from autoai_ts_libs.utils.messages.messages import Messages

import pandas as pd
import numpy as np
from numpy import array
import logging

tslogger = logging.getLogger(__name__)

#Constant value of input data limitations for pre-assessment of customer cluster setup
UPPER_BOUND_INPUT_DATA_SIZE_FOR_SMALL_TSHIRT_SIZE = 100000
UPPER_BOUND_INPUT_DATA_SIZE_FOR_MEDIUM_TSHIRT_SIZE = 300000
UPPER_BOUND_INPUT_DATA_SIZE_FOR_LARGE_TSHIRT_SIZE = 1000000

def make_holdout_split(
        dataset: pd.DataFrame,
        target_columns: Union[list, int, str],
        learning_type: str = "forecasting",
        test_size: Union[float, int] = 20,
        feature_columns: Union[list, int, str] = -1,
        timestamp_column: Union[int, float, str] = -1,
        lookback_window: int = 0,
        return_only_holdout: bool = False,
        test_dataset: pd.DataFrame = None,
        tshirt_size: str = "M",
        warn_msg: list = [],
        return_indices: bool = True
) -> Union[Tuple[array, array, array, array], Tuple[array, array, array, array, array, array, array, array]]:
    """
        This function is dedicated to split data into both training and holdout for time series
    Parameters
    ----------
    dataset: DataFrame, required
        A pandas dataframe
    target_columns: int or str, required
        Index or names of target time series in df
    learning_type: str
        Default "forecasting". Only "forecasting" is supported currently.
    test_size: float or int, optional
        Default 20. If float, between 0 and 1, indicates the radio of houldout dataset to the entire data. If int, represents the
        absolute number of houldout samples.
    feature_columns: int or str, optional
        Index or names of features in df
    timestamp_column: int or str, optional
        Index or name of timestamp column in df
    lookback_window: int, optional
        Default 0. The past date/time range to train the model and generate pipelines.
    return_only_holdout: bool, optional
        Default False. If set to True it will return only holdout dataset and indices but without training dataset and indices.
    test_dataset: DataFrame, Optional
        Default None, only used for providing user customized holdout dataset.
    tshirt_size: str. "S","M" or "L", optional
        Default "M".
    warn_msg: list, optional
        Default empty list, collection of warning messages popped up during execution
    return_indices: bool, optional
        Default True, indicator of result including indices of training and holdout
    Returns
    -------
    Numpy arrays:
        x_train, x_holdout,
        y_train, y_holdout,
        x_train_indices, x_holdout_indices,
        y_train_indices, y_holdout_indices
        if return_only_holdout:
            x_holdout, y_holdout,
            x_holdout_indices, y_holdout_indices
    """
    if dataset is None:
        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0069E'))

    if learning_type not in ("forecasting", ):
        raise Exception(Messages.get_message(learning_type, message_id='AUTOAITSLIBS0068E'))

    if test_dataset is not None:
        _validate_training_holdout_metadata(dataset,test_dataset)
        test_size = len(test_dataset)

    n_samples = len(dataset)
    if test_dataset is None:        
        if (test_size < 1 and test_size > 1/3) or (test_size > n_samples/3) or (test_size <= 0):
            raise Exception(Messages.get_message(test_size, n_samples, message_id='AUTOAITSLIBS0070E'))
    else:
        if test_size <= 0:
            raise Exception(Messages.get_message(test_size, n_samples, message_id='AUTOAITSLIBS0070E'))

    test_size_type = np.asarray(test_size).dtype.kind
    holdout_size = int(n_samples * test_size) if (test_size_type == 'f' and test_size < 1) else int(test_size)

    if not isinstance(target_columns, list):
        target_columns = [target_columns]

    if not isinstance(feature_columns, list):
        if feature_columns != -1:
            feature_columns = [feature_columns]
        else:
            feature_columns = []

    df = dataset
    holdout_df = test_dataset
    data_cols, time_col, used_cols = None, None, None
    fet_cols = []

    # Support string targets
    df_columns = df.columns.to_list()
    target_column_indexs = []
    for target in target_columns:
        if isinstance(target, int):
            target_column_indexs.append(target)
        elif isinstance(target, str):
            if target in df_columns:
                target_column_indexs.append(df_columns.index(target))
            else:
                # Warning
                print("target: %s is invalid" % (target))
        elif isinstance(target, float):
            target_column_indexs.append(int(target))

    target_columns = target_column_indexs

    if len(target_columns) == 0:
        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0072E'))

    # Support string features
    feature_column_indexs = []
    for feature in feature_columns:
        if isinstance(feature, int):
            feature_column_indexs.append(feature)
        elif isinstance(feature, str):
            if feature in df_columns:
                feature_column_indexs.append(df_columns.index(feature))
            else:
                # Warning
                print("feature: %s is invalid" % (feature))
        elif isinstance(feature, float):
            feature_column_indexs.append(int(feature))

    feature_columns = feature_column_indexs

    # Support string timestamp
    timestamp_column_index = -1
    if isinstance(timestamp_column, int):
        timestamp_column_index = timestamp_column
    elif isinstance(timestamp_column, str):
        if timestamp_column in df_columns:
            timestamp_column_index = df_columns.index(timestamp_column)
        else:
            # Warning
            print("timestamp_column: %s is invalid" % (timestamp_column))
    elif isinstance(timestamp_column, float):
        timestamp_column_index = int(timestamp_column)

    timestamp_column = timestamp_column_index


    if timestamp_column != -1:
        time_col = df.columns[timestamp_column]

    for i in target_columns:
        if i < 0 or i > (len(df.columns) - 1):
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0072E'))
        if pd.api.types.is_string_dtype(df.dtypes[i]):
            try:
                target_name = df.columns[i]
                df[target_name] = df[target_name].map(
                    lambda tar: str(tar).strip('\"')
                )
                df[target_name] = df[target_name].map(
                    lambda x: float(x) if len(x) != 0 else float('nan')
                )
            except Exception as ex:
                raise Exception(Messages.get_message(target_name, str(ex), message_id='AUTOAITSLIBS0073E'))
    tgt_cols = [df.columns.to_list()[i] for i in target_columns]

    if time_col is not None and time_col in tgt_cols:
        raise Exception(Messages.get_message(time_col, message_id='AUTOAITSLIBS0074E'))

    if time_col is not None:
        if (True in df.duplicated(subset=[time_col]).to_list()):
            raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0075E'))

        if holdout_df is not None:
            _parse_time_col(df, time_col, 1)
            _parse_time_col(holdout_df, time_col, 2)
        else:
            _parse_time_col(df, time_col)

        # ensure data sorted by time
        df = df.sort_values(by=time_col)
        if holdout_df is not None:
            _validate_time_interval(df, time_col, warn_msg, 1)
            holdout_df = holdout_df.sort_values(by=time_col)
            _validate_time(df, holdout_df, time_col)
            _validate_time_interval(holdout_df, time_col, warn_msg, 2)
            holdout_df, holdout_size = _validate_holdout_len(df, holdout_df, holdout_size, warn_msg)
            df = pd.concat([df, holdout_df], ignore_index=True, sort=False)

        _validate_time_interval(df, time_col, warn_msg)
    else:
        if holdout_df is not None:
            holdout_df, holdout_size = _validate_holdout_len(df, holdout_df, holdout_size, warn_msg)
            df = pd.concat([df, holdout_df], ignore_index=True, sort=False)

    _validate_data_len(tshirt_size, df, warn_msg)

    if len(feature_columns) > 0:
        fet_cols = [df.columns.to_list()[i] for i in feature_columns]

    # prepare data_cols and all_cols (= data_cols + time)
    data_cols = []
    for item in fet_cols:
        data_cols.append(item)
    for item in tgt_cols:
        if item not in data_cols:
            data_cols.append(item)

    if time_col is not None:
        used_cols = [time_col] + data_cols
    else:
        used_cols = data_cols

    # prepare data for training and testing
    loaded_data = df[used_cols]
    X_ = loaded_data[data_cols].to_numpy()
    y_ = loaded_data[tgt_cols].to_numpy()

    X, y = (
        X_.astype(float).reshape(-1, max(1, len(data_cols))),
        y_.astype(float).reshape(-1, max(1, len(tgt_cols))),
    )

    training_size = len(X_) - holdout_size
    data = {}
    data["X_train"], data["y_train"] = (
        X[: training_size, :],
        y[: training_size, :],
    )
    data["X_train_indices"], data["y_train_indices"] = (
        np.array(range(0, training_size)),
        np.array(range(0, training_size))
    )

    data["X_test"], data["y_test"] = (
        X[training_size - lookback_window:, :],
        y[training_size:, :],
    )
    data["X_test_indices"], data["y_test_indices"] = (
        np.array(range(training_size - lookback_window, len(X))),
        np.array(range(training_size, len(y)))
    )

    if return_only_holdout:
        if return_indices:
            return data["X_test"], data["y_test"], \
                   data["X_test_indices"], data["y_test_indices"]
        else:
            return data["X_test"], data["y_test"]
    else:
        if return_indices:
            return data["X_train"], data["X_test"], \
                   data["y_train"], data["y_test"], \
                   data["X_train_indices"], data["X_test_indices"], \
                   data["y_train_indices"], data["y_test_indices"]
        else:
            return data["X_train"], data["X_test"], \
                   data["y_train"], data["y_test"]

def _parse_time_col(data_df,time_col,df_type=0):
    if pd.api.types.is_numeric_dtype(data_df[time_col]):
        # nothing to do, assuming unix timestamp
        pass
    elif pd.api.types.is_string_dtype(data_df[time_col]):
        # check string format, and convert to unix timestamp
        try:
            from dateutil.parser import parse

            data_df[time_col] = data_df[time_col].map(
                lambda ts: parse((str(ts)).strip('\"'), fuzzy=False)
            )
        except Exception as e:
            try:
                from dateutil.parser import isoparser, isoparse
                data_df[time_col] = data_df[time_col].map(
                    lambda ts: isoparse((str(ts)).strip('\"'))
                )
            except Exception as ex:
                if df_type == 0:  # all data
                    raise Exception(Messages.get_message(time_col, "", message_id='AUTOAITSLIBS0076E'))
                elif df_type == 1:  # training data
                    raise Exception(Messages.get_message(time_col, " in the training data", message_id='AUTOAITSLIBS0076E'))
                elif df_type == 2:  # holdout data
                    raise Exception(Messages.get_message(time_col, " in the holdout data", message_id='AUTOAITSLIBS0076E'))
    else:
        # don't know how to handle, raise error
        if df_type == 0:  # all data
            raise Exception(Messages.get_message("", message_id='AUTOAITSLIBS0077E'))
        elif df_type == 1:  # training data
            raise Exception(Messages.get_message(" in the training data", message_id='AUTOAITSLIBS0077E'))
        elif df_type == 2:  # holdout data
            raise Exception(Messages.get_message(" in the holdout data", message_id='AUTOAITSLIBS0077E'))

def _validate_time_interval(df,time_col,warn_msg,df_type=0):
    # calculate relative standard deviation (in seconds) of successive timestamp deltas
    timestamps = df[time_col].to_list()
    timedeltas = []
    for i in range(1, len(timestamps)):
        diff = timestamps[i] - timestamps[i - 1]
        if type(diff) == pd._libs.tslibs.timedeltas.Timedelta:
            timedeltas.append(diff.total_seconds())
        else:
            timedeltas.append(diff)
    import statistics

    m = statistics.mean(timedeltas)
    s = statistics.stdev(timedeltas)
    if m == 0:
        if df_type == 0:  # all data
            raise Exception(Messages.get_message(time_col, "", message_id='AUTOAITSLIBS0071E'))
        elif df_type == 1:  # training data
            raise Exception(Messages.get_message(time_col, " in the training data", message_id='AUTOAITSLIBS0071E'))
        elif df_type == 2:  # holdout data
            raise Exception(Messages.get_message(time_col, " in the holdout data", message_id='AUTOAITSLIBS0071E'))

    r = 100.0 * s / m
    if r > 20.0:
        if df_type == 0:  # all data
            warn_msg.append(Messages.get_message("", message_id='AUTOAITSLIBS0004W'))
        elif df_type == 1:  # training data
            warn_msg.append(Messages.get_message(" in the training data", message_id='AUTOAITSLIBS0004W'))
        elif df_type == 2:  # holdout data
            warn_msg.append(Messages.get_message(" in the holdout data", message_id='AUTOAITSLIBS0004W'))

def _validate_time(train_df,holdout_df,time_col):
    if train_df[time_col].iat[-1] > holdout_df[time_col].iat[0]:
        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0087E'))

def _validate_data_len(tshirt_size,df, warn_msg):
    df_len = len(df)
    if df_len < 8:
        raise Exception(Messages.get_message(message_id='AUTOAITSLIBS0084E'))

    if df_len <= 36:
        warn_msg.append(Messages.get_message(message_id='AUTOAITSLIBS0007W'))
        
    # Add input data Limitation for pre-assessment of customer cluster setup.
    if tshirt_size == "M" and df_len > UPPER_BOUND_INPUT_DATA_SIZE_FOR_MEDIUM_TSHIRT_SIZE:
        df = df.tail(UPPER_BOUND_INPUT_DATA_SIZE_FOR_MEDIUM_TSHIRT_SIZE)
        warn_msg.append(Messages.get_message(str(UPPER_BOUND_INPUT_DATA_SIZE_FOR_MEDIUM_TSHIRT_SIZE),message_id='AUTOAITSLIBS0005W'))

    if tshirt_size == "S" and df_len > UPPER_BOUND_INPUT_DATA_SIZE_FOR_SMALL_TSHIRT_SIZE:
        df = df.tail(UPPER_BOUND_INPUT_DATA_SIZE_FOR_SMALL_TSHIRT_SIZE)
        warn_msg.append(Messages.get_message(str(UPPER_BOUND_INPUT_DATA_SIZE_FOR_SMALL_TSHIRT_SIZE),message_id='AUTOAITSLIBS0005W'))

    if tshirt_size == "L" and df_len > UPPER_BOUND_INPUT_DATA_SIZE_FOR_LARGE_TSHIRT_SIZE:
        df = df.tail(UPPER_BOUND_INPUT_DATA_SIZE_FOR_LARGE_TSHIRT_SIZE)
        warn_msg.append(Messages.get_message(str(UPPER_BOUND_INPUT_DATA_SIZE_FOR_LARGE_TSHIRT_SIZE),message_id='AUTOAITSLIBS0005W'))
    return df

def _validate_holdout_len(df, holdout_df, holdout_size, warn_msg):
    ratio_threshold = 1/3
    len_threshold = (len(df) + len(holdout_df)) / 3
    if (holdout_size < 1 and holdout_size > ratio_threshold) or\
            (holdout_size > len_threshold):
        if holdout_size < 1:
            holdout_size = ratio_threshold
            holdout_df = holdout_df.head(int(len_threshold))
        else:
            holdout_size = len_threshold
            holdout_df = holdout_df.head(int(len_threshold))
        warn_msg.append(Messages.get_message(message_id='AUTOAITSLIBS0006W'))
    return holdout_df, holdout_size

def _validate_training_holdout_metadata(df, holdout_df):
    if df.shape[1] != holdout_df.shape[1]:
        raise Exception(Messages.get_message(holdout_df.shape[1], df.shape[1], message_id='AUTOAITSLIBS0081E'))
    if list(df.columns) != list(holdout_df.columns):
        raise Exception(Messages.get_message(
            list(holdout_df.columns), list(df.columns),message_id='AUTOAITSLIBS0082E'))

