import pandas as pd

def shift_daily_crypto_compare_signal(hourly_data = None, ssj=None, local_root_directory=None, shift = 1, starting_date=None, running_date=None, frequence='daily'):

    hourly_data = hourly_data.drop_duplicates()

    hourly_data['date'] = pd.to_datetime(hourly_data.index)
    hourly_data['datetime'] = hourly_data.index.date
    hourly_data['hour'] = hourly_data.index.hour

    hourly_data['trigger']  = hourly_data['hour'] == shift
    hourly_data['datetime'] = hourly_data['datetime'].shift(shift)
    hourly_data['trigger'] = hourly_data['trigger'].cumsum()
    hourly_data = hourly_data.dropna()
    # aggregate by datetime and trigger : it should be the same
    hourly_data = hourly_data.groupby(['datetime']).agg({'date':'min', 'close': 'last', 'high': 'max', 'low': 'min', 'open': 'first', 'volumefrom': 'sum', 'volumeto' : 'sum'})
    hourly_data = hourly_data.drop_duplicates()
    hourly_data.index = hourly_data['date']
    hourly_data = hourly_data.drop(columns = ['date'])

    return hourly_data




