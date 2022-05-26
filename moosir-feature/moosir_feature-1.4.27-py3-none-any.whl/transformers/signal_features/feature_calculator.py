import pandas as pd
import numpy as np

from .core import *

FEATURE_PREFIX = "SIG"

FEATURES_SCHEMA_DICS = {"Peaks_All": ["Peaks_All"],
                        "Troughs_All": ["Troughs_All"]
                        }

FEATURES_SETTINGS_DICS = {"Peaks_All": {"extreme_n": 10,
                                        "polyorder": 3,
                                        "smoothing_win_len_perc": 0.20,
                                        "col_name":"SIG-Peaks_All"
                                        },
                          "Troughs_All": {"extreme_n": 10,
                                        "polyorder": 3,
                                        "smoothing_win_len_perc": 0.20,
                                        "col_name":"SIG-Troughs_All"
                                        },
                          }

FEATURES_CALC_DICS = {"Peaks_All": peaks_all,
                       "Troughs_All": troughs_all
                        }

FEATURE_FWD_PREFIX = "Fwd"

def _get_feature_col_name(prefix: str, win_len: int, orig_col_name: str):
    return f"{prefix}{'' if prefix == '' else '-'}{orig_col_name}-{win_len}"


def get_feature_col_full_names(feature_name: str, win_len: int):
    if feature_name in ["Peaks_All", "Troughs_All"]:
        settings = FEATURES_SETTINGS_DICS[feature_name]
        col_pref = settings["col_name"]
        extreme_n = settings["extreme_n"]
        cols = []
        for i in range(extreme_n):
            col = find_extreme_get_col_name(col_name_prefix=col_pref, extreme_ind=i, win_len=win_len)
            cols.append(col)
        return cols

    result = [_get_feature_col_name(prefix=FEATURE_PREFIX, win_len=win_len, orig_col_name=k)
              for k in
              FEATURES_SCHEMA_DICS[feature_name]]
    return result


def get_feature_col_by_subtype_name(feature_name: str, columns: list, is_fwd: bool):
    for col in columns:
        if feature_name in col:
            if is_fwd:
                if FEATURE_FWD_PREFIX in col:
                    return col
            else:
                return col
    raise Exception(f"column not found: {feature_name}")

def get_feature_lag_full_name(feature_name: str, win_len: int, lag_len: int):
    col_names = get_feature_col_full_names(feature_name=feature_name, win_len=win_len)
    results = [f"{col_name}_Lag-{lag_len}" for col_name in col_names]
    return results


def get_feature_fwd_full_name(feature_name: str, win_len: int, fwd_len: int):
    col_names = get_feature_col_full_names(feature_name=feature_name, win_len=win_len)
    results = [f"{col_name}_{FEATURE_FWD_PREFIX}-{fwd_len}" for col_name in col_names]
    return results


def validate_columns(data: pd.DataFrame,
                     feature_names: list,
                     win_lens: list,
                     lag_lens: list = None,
                     forward_lens: list = None):
    assert lag_lens is None or forward_lens is None, "forwards and lags cant be not none at the same time"

    cols = data.columns
    for f in feature_names:
        for w in win_lens:
            if lag_lens:
                for lag in lag_lens:
                    col_names = get_feature_lag_full_name(feature_name=f, win_len=w, lag_len=lag)
                    for col in col_names:
                        assert col in cols, f"missing column {col}"
            elif forward_lens:
                for fwd in forward_lens:
                    col_names = get_feature_fwd_full_name(feature_name=f, win_len=w, fwd_len=fwd)
                    for col in col_names:
                        assert col in cols, f"missing column {col}"
            else:
                col_names = get_feature_col_full_names(feature_name=f, win_len=w)
                for col in col_names:
                    assert col in cols, f"missing column {col}"
    return True


def calc_rolling_feature(ohlc: pd.DataFrame, win_len=10, selected_features=["Peaks_All"],
                         output_col_prefix=FEATURE_PREFIX, verbose=False):
    """
        applies one feature on input data rolling wind
        Note: tsfresh feature result cant be pandas per window
    """
    if verbose:
        print("#######################")
        print("prepare data for signals")
        print("#######################")
    # data = ohlc[["Close"]]
    data = ohlc.copy()
    assert data.index.name == "Timestamp"

    sig_data = data
    if verbose:
        print("#######################")
        print("calculate features")
        print("#######################")


    features_ls = []
    for feature in selected_features:
        arg_vals = {"ohlc": ohlc, "win_len": win_len}
        arg_vals.update(FEATURES_SETTINGS_DICS[feature])
        features_ls.append(FEATURES_CALC_DICS[feature](**arg_vals))

    features_df = pd.concat(features_ls, axis=1)

    assert len(features_df) + win_len == 1 + len(
        data), f"some data missed during calculation. lengths: input {len(data)}, result {len(features_df)}, window: {win_len} "

    return features_df
