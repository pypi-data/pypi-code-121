import pandas as pd
import numpy as np
import scipy.signal as signal

def _find_extreme_inds(data: np.ndarray, comparer=np.greater):
    return signal.argrelextrema(data, comparer)

def troughs_all(ohlc: pd.DataFrame,
                win_len: int,
                extreme_n: int,
                polyorder: int,
                smoothing_win_len_perc: float,
                col_name: str
                ):
    """
    - find n number of troughs in the window (wind len) after smoothing
    - returns distance to last low price in the window (not-normalized by current price)
    """
    assert "Low" in ohlc.columns, "column Low is missing"
    data = ohlc[["Low"]].copy()
    troughs = find_extreme(data=data,
                           win_len=win_len,
                           extreme_n=extreme_n,
                           polyorder=polyorder,
                           smoothing_win_len_perc=smoothing_win_len_perc,
                           comparer=np.less,
                           col_name=col_name)

    return troughs


def peaks_all(ohlc: pd.DataFrame,
              win_len: int,
              extreme_n: int,
              polyorder: int,
              smoothing_win_len_perc: float,
              col_name: str
              ):
    """
        - find n number of peaks in the window (wind len) after smoothing
        - returns distance to last high price in the window (not normalized by current price)
    """

    assert "High" in ohlc.columns, "column High is missing"
    data = ohlc[["High"]].copy()
    peaks = find_extreme(data=data,
                         win_len=win_len,
                         extreme_n=extreme_n,
                         polyorder=polyorder,
                         smoothing_win_len_perc=smoothing_win_len_perc,
                         comparer=np.greater,
                         col_name=col_name)

    return peaks

def find_extreme_get_col_name(col_name_prefix, extreme_ind, win_len):
    return f"{col_name_prefix}_{extreme_ind}-{win_len}"


def find_extreme(data: pd.DataFrame,
                 win_len: int,
                 extreme_n: int,
                 polyorder: int,
                 smoothing_win_len_perc: float,
                 comparer,
                 col_name: str):

    def _find_extreme(win: pd.DataFrame,
                      extreme_n: int,
                      polyorder: int,
                      smoothing_win_len_perc: float,
                      comparer):
        # return 1
        df = data.loc[win.index]
        win_data = df["_data"]

        smooth_win_len = int(len(win_data) * smoothing_win_len_perc)
        if smooth_win_len % 2 == 0:
            smooth_win_len = smooth_win_len + 1
        if smooth_win_len < polyorder:
            polyorder = smooth_win_len - 1

        smooth_d = signal.savgol_filter(win_data, window_length=smooth_win_len, polyorder=polyorder)
        inds = _find_extreme_inds(data=smooth_d, comparer=comparer)
        peaks = win_data.iloc[inds].values.reshape(-1)
        peaks = peaks - win_data.iloc[-1]

        last_row = data.loc[win.index].iloc[-1]
        for i in range(extreme_n):
            if i < len(peaks):
                # todo: shame
                col = find_extreme_get_col_name(col_name_prefix=col_name, extreme_ind=i, win_len=win_len)
                last_row[col]=peaks[i]

        result.append(last_row)

        return 1

    data.columns = ["_data"]

    for i in range(extreme_n):
        col = find_extreme_get_col_name(col_name_prefix=col_name, extreme_ind=i, win_len=win_len)
        data[col] = np.nan

    result = []
    _ = data.rolling(window=win_len).apply(lambda x: _find_extreme(win=x,
                                                                   extreme_n=extreme_n,
                                                                   polyorder=polyorder,
                                                                   smoothing_win_len_perc=smoothing_win_len_perc,
                                                                   comparer=comparer)
                                       , raw=False)
    result_df = pd.DataFrame(result)

    _ = result_df.pop("_data")

    return result_df