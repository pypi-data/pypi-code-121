import pandas as pd
from commodutil import transforms


def seasonalise(df, histfreq):
    """
    Given a dataframe, seasonalise the data, returning seasonalised dataframe
    :param df:
    :return:
    """
    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    if histfreq is None:
        histfreq = pd.infer_freq(df.index)
        if histfreq is None:
            histfreq = "D"  # sometimes infer_freq returns null - assume mostly will be a daily series

    if histfreq.startswith("W"):
        seas = transforms.seasonalise_weekly(df, freq=histfreq)
    else:
        seas = transforms.seasonailse(df)

    seas = seas.dropna(how="all", axis=1)  # dont plot empty years
    return seas
