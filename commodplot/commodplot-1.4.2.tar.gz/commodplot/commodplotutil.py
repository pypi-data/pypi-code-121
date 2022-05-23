import pandas as pd
from commodutil import dates
from commodutil import transforms

default_line_col = "khaki"

# try to put deeper colours for recent years, lighter colours for older years
year_col_map = {
    -10: "wheat",
    -9: "burlywood",
    -8: "steelblue",
    -7: "aquamarine",
    -6: "orange",
    -5: "yellow",
    -4: "saddlebrown",
    -3: "mediumblue",
    -2: "darkgreen",
    -1: "coral",
    0: "black",
    1: "red",
    2: "firebrick",
    3: "darkred",
    4: "crimson",
}


def gen_title(df, **kwargs):
    title = kwargs.get("title", "")
    title_postfix = kwargs.get("title_postfix", "")
    inc_change_sum = kwargs.get("inc_change_sum", True)
    if inc_change_sum:
        if title:
            if title_postfix:
                title = "{}  {}: {}".format(title, title_postfix, delta_summary_str(df))
            else:
                title = "{}   {}".format(title, delta_summary_str(df))
        else:
            if title_postfix:
                title = "{}   {}".format(title_postfix, delta_summary_str(df))
            else:
                title = delta_summary_str(df)
    else:
        if title:
            if title_postfix:
                title = "{}  {}".format(title, title_postfix)
            else:
                title = title

    return title


def seas_table(hist, fwd=None):
    hist = hist.resample("MS").mean()

    if fwd is not None and fwd.index[0] == hist.index[-1]:
        hist = hist[:-1]
        df = pd.concat([hist, fwd], sort=False)
    else:
        df = hist

    df = transforms.seasonailse(df)

    summary = df.resample("Q").mean()
    winter = summary.iloc[[0, 3], :].mean()
    winter.name = "Q1+Q4"
    summer = summary.iloc[[1, 2], :].mean()
    summer.name = "Q2+Q3"
    summary.index = ["Q1", "Q2", "Q3", "Q4"]
    summary = summary.append(winter)
    summary = summary.append(summer)
    cal = df.resample("Y").mean().iloc[0]
    cal.name = "Year"
    summary = summary.append(cal)
    summary = summary.round(2)

    df.index = df.index.strftime("%b")
    df = pd.concat([df, summary], sort=False).round(2)
    return df


def delta_summary_str(df):
    """
    Given a timeseries, produce a string which shows the latest change
    For example if T-1 value is 50 and T-2 is 45, return 50.00  △: +5
    """
    if isinstance(df, pd.DataFrame):
        df = pd.Series(df[df.columns[0]])

    df = df.dropna()
    val1 = df.iloc[-1]
    val2 = df.iloc[-2]
    delta = (val1 - val2).round(2)
    symb = "+" if delta > 0.0 else ""

    s = "{}   △: {}{}".format(val1.round(2), symb, delta)
    return s


def format_date_col(col, date_format="%d-%b"):
    """
    Format a column heading as a data
    :param col:
    :param date_format:
    :return:
    """
    try:
        if isinstance(col, str):
            col = pd.to_datetime(col).strftime(date_format)
        if isinstance(col, pd.Timestamp):
            col = col.strftime(date_format)
    except Exception:
        pass  # ignore - just return original

    return col


def reindex_year_df_rel_col(df):
    """
    Given a reindexed year dataframe, figure out which column to use for change summary
    Basic algorithm is use current year, unless you are 10 days from end of dataframe
    :param df:
    :return:
    """
    res_col = df.columns[0]

    years = dates.find_year(df)
    last_val_date = df.index[-1]

    colyears = [x for x in df if str(dates.curyear) in str(x)]
    if len(colyears) > 0:
        res_col = colyears[0]
        relyear = pd.to_datetime(
            "{}-01-01".format(years.get(res_col))
        )  # year of this column

        dft = df[colyears].dropna()
        if len(dft) > 0:
            relcol_date = df[res_col].dropna().index[-1]  # last date of this column

            delta = last_val_date - relcol_date
            if delta.days < 10:
                relyear1 = (relyear + pd.DateOffset(years=1)).year
                relyear1 = [x for x in df.columns if str(relyear1) in str(x)]
                if len(relyear1) > 0:
                    return relyear1[0]
            else:
                return res_col

    return res_col


def infer_freq(df):
    histfreq = (
        "D"  # sometimes infer_freq returns null - assume mostly will be a daily series
    )
    if df is not None:
        histfreq = pd.infer_freq(df.index)

    return histfreq


def std_yr_col(df, asdict=False):
    """
    Given a dataframe with yearly columns, determine the line colour to use
    """

    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)

    yearmap = dates.find_year(df, use_delta=True)
    colmap = {}
    for colname, delta in yearmap.items():
        colmap[colname] = year_col_map.get(delta, default_line_col)

    if asdict:
        return colmap

    # return array of colours to use - this can be passed into cufflift iplot method
    return [colmap[x] for x in df]
