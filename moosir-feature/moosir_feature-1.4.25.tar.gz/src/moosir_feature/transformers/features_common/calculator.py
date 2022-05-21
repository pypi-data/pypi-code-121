import pandas as pd


def align_features_and_targets(features: pd.DataFrame, targets: pd.DataFrame):
    if len(features) == 0 or len(targets) == 0:
        return [], [], []

    all = features.join(targets, how="inner")

    features = all[features.columns]
    targets = all[targets.columns]
    return features, targets, all


def combine_features(features_list: list) -> pd.DataFrame:
    """
    combine array of dataframes containing features
    joining on indexes
    """

    features_list = [f for f in features_list if len(f) > 0]

    if len(features_list) == 0:
        return features_list

    results = pd.concat(features_list, join='inner', axis=1)
    return results


def _get_lag_col_name(feature_col: str, lag_len: int):
    return f"{feature_col}-lag_{lag_len}"


def _apply_lag_full_col_name(features: pd.DataFrame, lag_feature_full_name: str, lag_len: str):
    features[_get_lag_col_name(feature_col=lag_feature_full_name, lag_len=lag_len)] = features[
        [lag_feature_full_name]].shift(
        lag_len)
    return features


def create_feature_lags(features: pd.DataFrame, targets: pd.DataFrame, lag_feature_start_with: str, lag_len: str):
    """
        Note: lags means multivariate!!!!
    """
    cols = features.columns[features.columns.str.startswith(lag_feature_start_with)]

    for col in cols:
        features = _apply_lag_full_col_name(features=features, lag_feature_full_name=col, lag_len=lag_len)

    features = features.iloc[lag_len:]
    targets = targets.iloc[lag_len:]
    return features, targets


def _drop_col_if_exists(data: pd.DataFrame, col_name: str):
    if not isinstance(data, pd.DataFrame):
        return data

    if col_name in data.columns:
        _ = data.pop(col_name)
    return data


def remove_ohlc_columns_if_exists(data: pd.DataFrame):
    _drop_col_if_exists(data=data, col_name="Open")
    _drop_col_if_exists(data=data, col_name="High")
    _drop_col_if_exists(data=data, col_name="Low")
    _drop_col_if_exists(data=data, col_name="Close")
    return data


def drop_na(features: pd.DataFrame, targets: pd.DataFrame):
    # print(features.describe())
    print(f"row loss due to NaN: {len(features) - len(features.dropna())}")
    features = features.dropna()

    features, targets, all = align_features_and_targets(features=features, targets=targets)
    return features, targets, all


def add_ohlc(data: pd.DataFrame, ohlc: pd.DataFrame):
    ohlc_cols = ["Open", "High", "Low", "Close"]
    remove_ohlc_columns_if_exists(data=data)
    result = combine_features(features_list=[ohlc, data])

    return result
