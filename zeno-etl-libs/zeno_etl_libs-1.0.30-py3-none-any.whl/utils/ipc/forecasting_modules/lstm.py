import datetime
import pandas as pd
import numpy as np
import keras.backend as K
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import LSTM
import tensorflow as tf
tf.__version__


def ae_weight_calc(y_true, y_pred, pos_error_weight):
    # dim of y_pred, y_true [n_batch, output var]
    error = y_true - y_pred
    greater = K.greater(error, 0)
    # 0 for y pred is more, 1 for y_pred is less
    greater = K.cast(greater, K.floatx())
    greater = greater + pos_error_weight

    error = K.abs(error)
    error = K.mean(error*greater, axis=1)

    return error


def custom_loss(pos_error_weight):

    def ae_specific_loss(y_true, y_pred):
        return ae_weight_calc(y_true, y_pred, pos_error_weight)

    # Returns the (y_true, y_pred) loss function
    return ae_specific_loss


# create a differenced series for stationarity
def difference(dataset, interval=1):
    diff = list()
    for i in range(interval, len(dataset)):
        value = dataset[i] - dataset[i - interval]
        diff.append(value)
    return pd.Series(diff)


def series_to_supervised(df, n_in=1, n_out=1, dropnan=True):
    if type(df) == pd.DataFrame:
        data = df[['net_sales_quantity']].values
    else:
        data = df
    data_df = pd.DataFrame(data)

    n_vars = 1
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(data_df.shift(i))
        names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(data_df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
    # put it all together
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


def prepare_data(df, n_test=1, n_in=1, n_out=1):
    np.random.seed(1234)
    # transform into lag and lead
    supervised_df = series_to_supervised(df, n_in=n_in, n_out=n_out)
    date_df = df[['date']].reset_index(drop=True)
    supervised_df = supervised_df.merge(
        date_df, how='inner', left_index=True, right_index=True)
    # marking test and train
    supervised_df['sample_flag'] = ''
    supervised_df.iloc[0:-n_test]['sample_flag'] = 'train'
    supervised_df.iloc[-n_test:]['sample_flag'] = 'validation'

    # transform data to be stationary
    raw_values = df[['net_sales_quantity']].values
    diff_series = difference(raw_values, 1)
    diff_values = diff_series.values
    diff_values = diff_values.reshape(len(diff_values), 1)
    # rescale values to -1, 1
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaled_values = scaler.fit_transform(diff_values)
    scaled_values = scaled_values.reshape(len(scaled_values), 1)
    # transform into supervised learning problem X, y
    supervised_scaled_df = series_to_supervised(
        scaled_values, n_in=n_in, n_out=n_out)
    supervised_scaled_df = supervised_scaled_df.merge(
        date_df, how='inner', left_index=True, right_index=True)
    # marking test and train for scaled version
    supervised_scaled_df['sample_flag'] = ''
    supervised_scaled_df.iloc[0:-n_test]['sample_flag'] = 'train'
    supervised_scaled_df.iloc[-n_test:]['sample_flag'] = 'validation'

    return supervised_df, supervised_scaled_df, scaler


# fit an LSTM network to training data
def fit_lstm(
    X, y, n_in=1, n_out=1, n_batch=1, nb_epoch=1000,
        n_neurons=4, use_dropout=False, error_factor=1):
    # reshape training into [samples, timesteps, features]
    X = X.reshape(X.shape[0], 1, X.shape[1])
    # design network
    model = Sequential()
    model.add(LSTM(
        n_neurons, batch_input_shape=(n_batch, X.shape[1], X.shape[2]),
        stateful=True))
    if use_dropout is not False:
        model.add(Dropout(use_dropout))
    model.add(Dense(y.shape[1]))
    loss = custom_loss(error_factor)
    model.compile(loss=loss, optimizer='adam')
#     print(model.summary())
#     model.compile(loss='mean_squared_error', optimizer='adam')
    # fit network
    for i in range(nb_epoch):
        model.fit(X, y, epochs=1, batch_size=n_batch, verbose=0, shuffle=False)
        model.reset_states()
    return model


# make one forecast with an LSTM,
def forecast_lstm(model, X, n_batch):
    # reshape input pattern to [samples, timesteps, features]
    forecasts = []
    # make forecast
    for i in range(X.shape[0]):
        X_input = X[i, :].reshape(1, n_batch, X.shape[1])
        forecast = model.predict(X_input, batch_size=n_batch)
        # convert to array
        forecasts.append(list(forecast.reshape(forecast.shape[1])))
    return forecasts


def inverse_transform(data_df, scaler, undifferenced_df, col_names):
    undifferenced_df = undifferenced_df.loc[data_df.index]

    for col in undifferenced_df.columns:
        if (data_df[col].dtype == float):
            data_df[col] = scaler.inverse_transform(data_df[[col]])
            data_df[col] += undifferenced_df[col]
    col_names = ['var1(t-1)'] + col_names
    for i in list((range(1, len(col_names)))):
        data_df[col_names[i]] = scaler.inverse_transform(
            data_df[[col_names[i]]])
        data_df[col_names[i]] += data_df[col_names[i - 1]]

    data_df[col_names] = np.round(data_df[col_names])

    return data_df


def lstm_horizon_ape(df, col_names):
    predicted = df[col_names].sum(axis=1)
    actual = df[[x.replace('_hat', '') for x in col_names]].sum(axis=1)
    return abs(predicted - actual)/actual


def lstm_forecast(
    df, n_neurons=1, week_in=1, week_out=1, forecast_horizon=4, epochs=90,
        use_dropout=False, n_batch=1, error_factor=1):

    drug_id = df['drug_id'].unique()[0]
    start_date = df.date.max()
    date_list = [
        start_date + datetime.timedelta(days=d*7)
        for d in range(1, forecast_horizon+1)]
    fcst = [0] * forecast_horizon

    # setting seed for reproducibility
    np.random.seed(1234)
    tf.random.set_seed(1234)

    supervised_df, supervised_scaled_df, scaler = prepare_data(
        df, n_test=forecast_horizon, n_in=week_in, n_out=4)
    train = supervised_scaled_df
    _, test, _ = prepare_data(
        df, n_test=forecast_horizon, n_in=week_in, n_out=0)

    variable_name = list(train.columns)
    variable_name = variable_name[:-2]
    X_train, y_train = (
        train[variable_name].values[:, 0:week_in],
        train[variable_name].values[:, week_in:])

    X_test = test[variable_name[:week_in]].iloc[-1]
    X_test = np.reshape(np.ravel(X_test), (1, X_test.shape[0]))

    model = fit_lstm(
        X_train, y_train, n_in=week_in, n_out=week_out, n_batch=n_batch,
        nb_epoch=epochs, n_neurons=n_neurons, use_dropout=use_dropout,
        error_factor=error_factor)

    hat_col = variable_name[week_in:]
    hat_col = [x + '_hat' for x in hat_col]

    scaler_test_fcst = forecast_lstm(model, X_test, n_batch=n_batch)
    test_fcst = scaler.inverse_transform(scaler_test_fcst)
    test_fcst = np.ravel(test_fcst)
    for i in range(len(test_fcst)):
        fcst[i] = df.net_sales_quantity.iloc[-1] + np.sum(test_fcst[:i])
        if fcst[i] < 0:
            fcst[i] = 0

    fcst_df = pd.DataFrame({
        'drug_id': drug_id, 'date': date_list, 'fcst': np.round(fcst),
        'std': np.round(df.net_sales_quantity.iloc[-8:].std())})

    return fcst_df


def lstm_wide_long(df, supervised_hat, hat_col):
    drug_id = df['drug_id'].values[0]
    supervised_hat = supervised_hat[supervised_hat['drug_id'] == drug_id]
    return_df = df.copy()
    fcst = (
        list(supervised_hat.iloc[:-1][hat_col[0]].values) +
        list(supervised_hat.iloc[-1][hat_col].values))
    return_df.loc[-len(fcst):, 'fcst'] = pd.Series(
        fcst, index=df.index[-len(fcst):])

    return return_df


def hinge_error(error):
    return sum(error < 0)