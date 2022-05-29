import pandas as pd
import numpy as np

from tsfresh.feature_extraction import settings
from tsfresh.utilities.dataframe_functions import roll_time_series
from tsfresh import extract_features


TSF_ID_COL = "Tsf_Id"
FEATURES_SCHEMA_DICS = {"linear_trend_timewise": ["Trend-Pvalue", "Trend-Rvalue", "Trend-Intercept", "Trend-Slope",
                                                  "Trend-Stderr"],
                        "abs_energy": ["Abs-energy"],
                        "benford_correlation": ["Benford-correlation"],
                        "binned_entropy": ["Binned-entropybin10"],
                        "c3": ["C3-laj1", "C3-laj2", "C3-laj3"],

                        # todo: not working, exceptions
                        # "fft_aggregated": ["Centroid", "Variance", "Skew", "Kurtosis"],
                        # "agg_autocorrelation": ["Mean_lag_x", "Median_lag_x", "Var_lag_x"],
                        # "absolute_sum_of_changes": ["Absolute_sum_of_changes"],
                        # "absolute_maximum": ["Absolute-maximum"],
                        }

FEATURE_PREFIX = "TS"


def _get_feature_col_name(prefix: str, win_len: int, orig_col_name: str):
    return f"{prefix}{'' if prefix == '' else '-'}{orig_col_name}-{win_len}"


def get_feature_col_full_name(feature_name: str, win_len: int):
    result = [_get_feature_col_name(prefix=FEATURE_PREFIX, win_len=win_len, orig_col_name=k)
              for k in
              FEATURES_SCHEMA_DICS[feature_name]]
    return result


def get_feature_col_by_subtype_name(feature_name: str, win_len: int, subtype_name: str, is_fwd: bool, fwd_len: -1):
    if is_fwd:
        alls = get_feature_fwd_full_name(feature_name=feature_name, win_len=win_len, fwd_len=fwd_len)
    else:
        alls = get_feature_col_full_name(feature_name=feature_name, win_len=win_len)

    # todo: contain is wrong here, proper break by '-' and has Fwd, lag logic
    for f in alls:
        if subtype_name in f:
            return f


def get_feature_lag_full_name(feature_name: str, win_len: int, lag_len: int):
    col_names = get_feature_col_full_name(feature_name=feature_name, win_len=win_len)
    results = [f"{col_name}_Lag-{lag_len}" for col_name in col_names]
    return results


def get_feature_fwd_full_name(feature_name: str, win_len: int, fwd_len: int):
    col_names = get_feature_col_full_name(feature_name=feature_name, win_len=win_len)
    results = [f"{col_name}_Fwd-{fwd_len}" for col_name in col_names]
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
                col_names = get_feature_col_full_name(feature_name=f, win_len=w)
                for col in col_names:
                    assert col in cols, f"missing column {col}"
    return True


def _tsf_preprocess_data(data: pd.DataFrame):
    # preprocess data
    tsf_data = data.copy()
    tsf_data[TSF_ID_COL] = 1
    tsf_data = tsf_data.reset_index()
    return tsf_data


def calc_rolling_feature(ohlc: pd.DataFrame, win_len=10, selected_features=["linear_trend_timewise"],
                         output_col_prefix=FEATURE_PREFIX, verbose=False):
    """
        applies one feature on input data rolling wind
        Note: tsfresh feature result cant be pandas per window
    """
    if verbose:
        print("#######################")
        print("prepare data for tsfresh")
        print("#######################")
    data = ohlc[["Close"]]
    assert data.index.name == "Timestamp"

    tsf_data = _tsf_preprocess_data(data=data)
    tsf_data = tsf_data.set_index("Timestamp")
    if verbose:
        print("#######################")
        print("prepare rolling windows")
        print("#######################")

    df_rolled = roll_time_series(tsf_data, column_id="Tsf_Id", max_timeshift=win_len, min_timeshift=win_len)

    # todo: need random timestamp index!!! otherwise, returns empty
    rand_indx = pd.date_range(start='1/1/2000', periods=len(df_rolled), freq="T")
    df_rolled.index = rand_indx
    df_rolled.index.name = "Timestamp"

    if verbose:
        print("#######################")
        print("calculate features")
        print("#######################")

    settings_comprehensive = settings.ComprehensiveFCParameters()

    selected_settings = {}
    selected_settings_cols = []
    for key in selected_features:
        selected_settings[key] = settings_comprehensive[key]
        selected_settings_cols = selected_settings_cols + get_feature_col_full_name(feature_name=key, win_len=win_len)

    kind_to_fc_parameters = {"Close": selected_settings}

    roll_features = extract_features(df_rolled,
                                     column_id="id",
                                     column_sort="sort",
                                     column_value="Close",
                                     kind_to_fc_parameters=kind_to_fc_parameters,
                                     show_warnings=True
                                     )
    if verbose:
        print("#######################")
        print("mapping output columns")
        print("#######################")

    roll_features.index.set_names(["Tsf_Id", "Ind"], inplace=True)
    roll_features = roll_features.swaplevel()
    roll_features = roll_features.reset_index(level=1)
    _ = roll_features.pop("Tsf_Id")

    roll_features["Timestamp"] = data.index[roll_features.index.values]
    roll_features = roll_features.reset_index().set_index("Timestamp")
    _ = roll_features.pop("Ind")

    roll_features.columns = selected_settings_cols

    roll_features = roll_features.join(data)

    # todo: this is wrong, it actually needs to be ... + win_len + 1 = len(data)!!!
    assert len(roll_features) + win_len == len(
        data), f"some data missed during calculation. lengths: input {len(data)}, result {len(roll_features)}, window: {win_len} "

    return roll_features


if __name__ == '__main__':
    DATA_PATH = r'C:\datalake-train\moosir\preproc\data\01_raw\close_market_data.csv'
    data = pd.read_csv(DATA_PATH, index_col="Timestamp", parse_dates=True)

    data = data.iloc[2000:2200]
    selected_features = ["linear_trend_timewise", "fft_aggregated"]
    res = calc_rolling_feature(data=data,
                               selected_features=selected_features)

    print(res)
