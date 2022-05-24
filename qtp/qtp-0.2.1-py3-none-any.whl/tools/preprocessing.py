import pandas as pd

def read_csv(csv_path):
    df = pd.read_csv(csv_path, dtype={'code':str}, parse_dates=['date'])
    df.index = df['code']
    df.drop(['code'], inplace=True, axis=1)
    return df

def shift_data(df, feature_names, days, type):
    turn = False
    if isinstance(feature_names, list):
        turn = True

    else:
        raise Exception("please confirm list type")

    if turn:
        days = days+1
        for feature_name in feature_names:
            if type == 'before':
                for day in range(1, days):
                    new_feature_name = feature_name + '-' + str(day)
                    df.loc[:, new_feature_name] = df[feature_name].shift(day)
            if type == 'after':
                for day in range(1, days):
                    new_feature_name = feature_name + '+' + str(day)
                    df.loc[:, new_feature_name] = df[feature_name].shift(-day)
        df.dropna(inplace=True)
        return df

def ratio_close_ma(df, ma):
    ma_name = 'ma' + str(ma)
    df[ma_name] = df['close'].rolling(ma).mean()
    df.loc[:, 'close-'+ma_name] =round(df['close'] / df[ma_name], 4)
    return df

def ratio_close_ema(df, ema):
    ema_name = 'ema' + str(ema)
    df[ema_name] = df['close'].ewm(span=ema, min_periods=1,
                                   adjust=False,ignore_na=False).mean()
    df.loc[:, 'close-'+ema_name] =round(df['close'] / df[ema_name], 4)
    return df

def ratio_volume_ma(df, ma):
    ma_name = 'vma' + str(ma)
    df[ma_name] = df['volume'].rolling(ma).mean()
    df.loc[:, 'volume-'+ma_name] =round(df['volume'] / df[ma_name], 4)
    return df

def ratio_candle(df):
    df.loc[:, 'close_open_ratio'] = round(df['close'] / df['open'], 4)
    df.loc[:, 'close_high_ratio'] = round(df['high'] / df['open'], 4)
    df.loc[:, 'close_low_ratio'] = round(df['low'] / df['open'], 4)

    # df.loc[df['close_open_ratio'] > 1.0000, 'candle_shape'] = 1
    # df.loc[df['close_open_ratio'] < 1.0000, 'candle_shape'] = 0
    # df.loc[df['close_open_ratio'] == 1.0000, 'candle_shape'] = 1
    return df

def find_features_startswith(df, name):
    name_contained = df.columns.str.startswith(name)
    columns = df.loc[:, name_contained].columns
    return columns

def find_features_contains(df, name):
    name_contained = df.columns.str.contains(name)
    columns = df.loc[:, name_contained].columns
    return columns

def find_features_endswith(df, name):
    name_contained = df.columns.str.endswith(name)
    columns = df.loc[:, name_contained].columns
    return columns

def max_of(df, feature_name, feature_names):
    name = feature_name + '_max'
    name_where = name + '_where'
    df.loc[:, name] = df.loc[:, feature_names].max(axis=1)
    df.loc[:, name_where] = df.loc[:, feature_names].idxmax(axis=1)
    return df

def min_of(df, feature_name, feature_names):
    name = feature_name + '_min'
    name_where = name + '_where'
    df.loc[:, name] = df.loc[:, feature_names].min(axis=1)
    df.loc[:, name_where] = df.loc[:, feature_names].idxmin(axis=1)
    return df

def time_splite(df):
    df.loc[:, 'year'] = df.index.year
    df.loc[:, 'month'] = df.index.month
    df.loc[:, 'day'] = df.index.day
    df.loc[:, 'hour'] = df.index.hour
    df.loc[:, 'minute'] = df.index.minute
    df.loc[:, 'second'] = df.index.second

    df.loc[:, 'y+m'] = df['year'].astype(str) + '-' + df['month'].astype(str)
    df.loc[:, 'y+m'] = pd.to_datetime(df['y+m'], errors='coerce')
    return df

def time_span(df, span="24h", base="9h"):
    df_span = pd.DataFrame()
    df_span['open'] = df['open'].resample(span, offset=base).first()
    df_span['high'] = df['high'].resample(span, offset=base).max()
    df_span['low'] = df['low'].resample(span, offset=base).min()
    df_span['close'] = df['close'].resample(span, offset=base).last()
    df_span['volume'] = df['volume'].resample(span, offset=base).sum()
    return df_span
