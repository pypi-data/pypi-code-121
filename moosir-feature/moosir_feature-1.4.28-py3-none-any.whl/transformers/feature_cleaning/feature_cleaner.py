"""
todo:
    - there is way more ways of removing outliers:  Peirce criterion, Grubb's test or Dixon's Q-test, clusters, zscore, ...


"""
import logging
import pandas as pd
from pandas.tseries.frequencies import to_offset
from sklearn.preprocessing import MinMaxScaler


logger = logging.getLogger(__file__)

def clip_quantile(features: pd.DataFrame, lower_quantile=0.01, upper_quantile=0.99):
    return features.clip(features.quantile(lower_quantile), features.quantile(upper_quantile), axis=1)


def _apply_timestamp_ohlc_resample(ohlc_row):

    if len(ohlc_row) == 0:
        # todo: potential unwanted data loss
        # happens normally with none inferable freq (e.x. datatimeindex with missing values like weekends)
        return

    row = ohlc_row.iloc[0].copy()
    row["Open"] = ohlc_row["Open"].iloc[0]
    row["Close"] = ohlc_row["Close"].iloc[-1]
    row["Low"] = ohlc_row["Low"].min()
    row["High"] = ohlc_row["High"].max()

    return row

def timestamp_ohlc_resample(ohlc: pd.DataFrame, resample_freq: str) -> pd.DataFrame:
    """
    - merging ohlc data during resampling
    - note that using first/last on higher frequency is wrong in ohlc context

    """
    assert sorted(["Open", "High", "Low", "Close"]) == sorted(ohlc.columns), "input missing/more ohlc required columns"
    # never use last() cos it hints the model for future
    # never use resample() cos it put nan for weekends and holidays
    requested_freq = to_offset(resample_freq)
    ohlc_freq = ohlc.index.freq

    if ohlc_freq is None:
        logger.warning("input ohlc does not have any frequency, will infer to validate")
        diffs = (ohlc.index[1:] - ohlc.index[:-1])
        ohlc_freq = to_offset(diffs[0])

    if requested_freq <= ohlc_freq:
        logger.warning(f"requested frequency is bigger than input ohlc frequency, no action: {requested_freq } <= {ohlc_freq} ")
        return ohlc

    # ohlc.index = pd.to_datetime(ohlc.index)

    resampled = (ohlc
                 .groupby(pd.Grouper(freq=resample_freq))
                 .apply(_apply_timestamp_ohlc_resample)
                  # for missing data (e.x. weekends) it still creates nan!!
                  # so, rows with all nan likely to be result of this group by - so, delete them all
                 .dropna(how="all")
                 )
    return resampled




def convert_to_pips(data: pd.DataFrame):
    return data.round(4).sub(1).mul(10000)


def apply_basic_cleaning(instances: pd.DataFrame, resample_freq: str):
    # basic transforms
    result = instances.copy()
    result = timestamp_ohlc_resample(ohlc=result, resample_freq=resample_freq)
    result = convert_to_pips(data=result)

    return result


def standardize(data: pd.DataFrame):
    """
    rescale all values to be have mean = 0 and std = 1
    z = (x- mean) / std
    Note:
        - Better not to use it cuz of any normalize assumption to financial data is dangerous (todo: to be confirmed)!!!
        - THE RESULT WILL BE NORMAL DISTRIBUTION
        - standard deviation and mean changed (unlike normalization)
        - z-score standardization
        - good for comparing data with different UoM
        - must for gradient descent based

    """
    raise Exception("Not implemented!!")


def normalize(data: pd.DataFrame):
    """
      rescale all values to be [0,1]
      z = (X - Xmin) / Xmax - Xmin
      Note:
          - DOES NOT change the distribution of the result
          - standard deviation and mean is not changed (unlike standardize)
          - MinMaxScaling is normalization
          - can suppress the effect of outliers (not sure)??
          - must for gradient descent based
          - not required for decision trees
          - you should scale target variable too!!!
      :param target_col: just to make sure that target col is not in this process
      """

    scaler = MinMaxScaler()
    scaler.fit(data)
    transformed = scaler.transform(data)

    transformed_df = pd.DataFrame(data=transformed, index=data.index, columns=data.columns)
    return transformed_df, scaler

