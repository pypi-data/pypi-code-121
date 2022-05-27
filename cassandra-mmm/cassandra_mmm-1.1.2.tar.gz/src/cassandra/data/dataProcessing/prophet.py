from cassandra.model.modelEvaluation.plot import show_seasonality
from prophet.plot import plot_plotly, plot_components_plotly
from prophet import Prophet
from cassandra.references.load_holidays import load_holidays
import pandas as pd
import warnings


def prophet(df, name_date_column, name_target_column, window_start='', window_end='',
            national_holidays_abbreviation='IT', future_dataframe_periods=14, plot_prophet=True, trend_seasonality=True,
            holidays_seasonality=True, daily_seasonality=True, weekly_seasonality=True, monthly_seasonality=True,
            yearly_seasonality=True, seasonality_mode='additive'):
    # Read the CSV on holidays
    warnings.filterwarnings("ignore")
    csv_holiday = load_holidays()

    # Select the holidays according to the country that interests me
    condition = (csv_holiday['country'] == national_holidays_abbreviation)
    holidays = csv_holiday.loc[condition, ['ds', 'holiday']]

    # Create a DF with the only two columns for Prophet
    prophet_df = df[[name_date_column, name_target_column]]

    # Rename the columns for Prophet
    prophet_df = prophet_df.rename(columns={name_date_column: 'ds', name_target_column: 'y'})

    # Instance and fit Prophet
    prophet_m = Prophet(weekly_seasonality=weekly_seasonality, yearly_seasonality=yearly_seasonality,
                        daily_seasonality=daily_seasonality, holidays=holidays, seasonality_mode=seasonality_mode)
    if monthly_seasonality:
        prophet_m.add_seasonality(name='monthly', period=30.5, fourier_order=5)
    prophet_m.fit(prophet_df)

    future = prophet_m.make_future_dataframe(periods=future_dataframe_periods)

    forecast = prophet_m.predict(future)

    new_forecast = forecast[['ds', 'yhat', 'trend', 'holidays', 'additive_terms', 'multiplicative_terms']].copy()

    if 'yearly' in forecast:
        new_forecast['yearly'] = forecast['yearly'].copy()
    if 'monthly' in forecast:
        new_forecast['monthly'] = forecast['monthly'].copy()
    if 'weekly' in forecast:
        new_forecast['weekly'] = forecast['weekly'].copy()
    if 'daily' in forecast:
        new_forecast['daily'] = forecast['daily'].copy()

    # if plot_prophet:
    # prophet_m.plot(forecast)
    # prophet_m.plot_components(forecast)
    # plot_components_plotly(prophet_m, forecast)

    sub_prophet_df = new_forecast[['ds']].copy()

    if trend_seasonality:
        sub_prophet_df['trend'] = new_forecast['trend']
    if holidays_seasonality:
        sub_prophet_df['holidays'] = new_forecast['holidays']
    if 'yearly' in new_forecast:
        sub_prophet_df['yearly'] = new_forecast['yearly']
    if 'monthly' in forecast:
        sub_prophet_df['monthly'] = new_forecast['monthly']
    if 'weekly' in forecast:
        sub_prophet_df['weekly'] = new_forecast['weekly']
    if 'daily' in forecast:
        sub_prophet_df['daily'] = new_forecast['daily']

    sub_prophet_df = sub_prophet_df.rename(columns={'ds': name_date_column})

    df[name_date_column] = pd.to_datetime(df[name_date_column])
    sub_prophet_df[name_date_column] = pd.to_datetime(sub_prophet_df[name_date_column])

    full_df = pd.merge(df, sub_prophet_df, how='inner', on=name_date_column)

    if window_start:
        full_df.drop(full_df[full_df[name_date_column] < window_start].index, inplace=True)
    if window_end:
        full_df.drop(full_df[full_df[name_date_column] > window_end].index, inplace=True)

    # aggiunto per il plot made in cassandra
    if plot_prophet:
        seasonality_columns = []
        if 'trend' in full_df.columns:
            seasonality_columns.append('trend')
        if 'holidays' in full_df.columns:
            seasonality_columns.append('holidays')
        if 'yearly' in full_df.columns:
            seasonality_columns.append('yearly')
        if 'monthly' in full_df.columns:
            seasonality_columns.append('monthly')
        if 'weekly' in full_df.columns:
            seasonality_columns.append('weekly')
        if 'daily' in full_df.columns:
            seasonality_columns.append('daily')
        show_seasonality(full_df, seasonality_columns, name_date_column)

    return full_df
