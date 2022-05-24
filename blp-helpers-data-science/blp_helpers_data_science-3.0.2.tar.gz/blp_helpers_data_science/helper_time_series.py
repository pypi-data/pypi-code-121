from sklearn.metrics import mean_squared_error
from numpy import sqrt
import seaborn as sns
import pandas as pd


def get_x_y_values(train, test, x_col, y_col):
    return train[x_col], train[y_col], test[x_col], test[y_col]


def get_train_test(data, test_size=0.66, viz=False, sort=False, return_array=False):
    """data: pandas.DataFrame where columns = features
    sort: whether data should be sorted (relevant as this is Ts)
    Returns train, test as pandas.DataFrame or numpy.ndarray depending on return_array
    """

    assert isinstance(data, pd.DataFrame)

    if data.shape[1] > 1:
        print('The dataframe has more than one column, sure that you have excluded the data-col?')
        print(data.head(3))

    orig_data = data.copy()

    if isinstance(test_size, float):
        train_size = 1 - test_size
        split_row = int(orig_data.shape[0]*train_size)
        train = orig_data[0:split_row]
        test = orig_data[split_row:]
    else:
        train_size = orig_data.shape[0]-test_size
        train = orig_data[0:train_size]
        test = orig_data[train_size:]

    assert (train.shape[0] + test.shape[0]) == orig_data.shape[0]

    if sort:
        # relevant as this is Ts
        print('not yet implemented')

    if viz:
        # to assert that the TS are continuos after plotting
        sns.lineplot(data=train, color='green')
        sns.lineplot(data=test, color='red')

    if return_array:
        train = train.to_numpy()
        test = test.to_numpy()

    return train, test


def get_lagged_values(data, calc_col, forecast_days, drop_na=True):
    """

    data = dataframe
    Returns a dataframe (reframed_prediction_horizon) where each column is the next value for the previous column


    don't drop NAs if I will only use test-set as test-set is not affected by the NAs (if test-set-split starts after
    train)

    Example:

    forecast_days = 7

    data:

        Date        temperature
    0   1981-01-01  20.7
    1   1981-01-02  17.9
    2   1981-01-03  18.8
    3   1981-01-04  14.6
    4   1981-01-05  15.8
    5   1981-01-06  15.8
    6   1981-01-07  15.8
    7   1981-01-08  17.4
    8   1981-01-09  21.8
    9   1981-01-10  20.0
    10  1981-01-11  16.2
    11  1981-01-12  13.3
    12  1981-01-13  16.7
    13  1981-01-14  21.5

    reframed_prediction_horizon:

    t       t+1     t+2     t+3     t+4     t+5     t+6     t+7
    NaN     20.7    17.9    18.8    14.6    15.8    15.8    15.8
    20.7    17.9    18.8    14.6    15.8    15.8    15.8    17.4
    17.9    18.8    14.6    15.8    15.8    15.8    17.4    21.8
    18.8    14.6    15.8    15.8    15.8    17.4    21.8    20.0
    14.6    15.8    15.8    15.8    17.4    21.8    20.0    16.2
    15.8    15.8    15.8    17.4    21.8    20.0    16.2    13.3
    15.8    15.8    17.4    21.8    20.0    16.2    13.3    16.7
    15.8    17.4    21.8    20.0    16.2    13.3    16.7    21.5
    17.4    21.8    20.0    16.2    13.3    16.7    21.5    25.0
    21.8    20.0    16.2    13.3    16.7    21.5    25.0    20.7
    20.0    16.2    13.3    16.7    21.5    25.0    20.7    20.6
    16.2    13.3    16.7    21.5    25.0    20.7    20.6    24.8
    13.3    16.7    21.5    25.0    20.7    20.6    24.8    17.7
    16.7    21.5    25.0    20.7    20.6    24.8    17.7    15.5
    """

    reframed_prediction_horizon = pd.DataFrame()
    prediction_base = data.copy()

    reframed_prediction_horizon[calc_col + '+0'] = prediction_base[calc_col].shift(1)
    reframed_prediction_horizon[calc_col + '+1'] = prediction_base[calc_col]

    for shift in range(1, forecast_days):
        reframed_prediction_horizon[calc_col + '+' + str(shift + 1)] = prediction_base[calc_col].shift(-shift)

    if drop_na:
        reframed_prediction_horizon = reframed_prediction_horizon.dropna().reset_index(drop=True)

    return reframed_prediction_horizon


def get_baseline(data, calc_col, viz=False, test_size=0.66, show_explanation=False, drop_na=True):
    """Uses persistence_algorithm to calc RMSE to get baseline value for forecasting performance
    data: pandas.DataFrame with calc_col
        calc_col: column that should be predicted

    # Steps in the persistence_algorithm

    1. Transformn into supervised problem (using one lag)
    2. Get test-data (inkl. x/y as this is a supervised problem now) (train will also be generated but not used for
    the predictions)
    3. Define persistence_algorithm; here: x=y, and x=y --> x=t0, y=t+1, i. e. the persistence_algorithm predicts the
    next value at any given step)
    4. Make forecast + calc rmse

    See: Introduction to Time Series Forecasting with Python How to Prepare Data and Develop Models to Predict the
    Future by Jason Brownlee
    """
    # convert into supervised problem (using one lag)

    assert isinstance(data, pd.DataFrame)
    data_orig = data.copy()

    data_new = get_lagged_values(data_orig, calc_col, 1, drop_na=drop_na)

    # get test-data
    train_data, test_data = get_train_test(data_new, test_size)

    # get x+y
    train_x, train_y, test_x, test_y = get_x_y_values(train_data, test_data, calc_col + '+0', calc_col + '+1')

    # get predictions using persistence_algorithm
    """if the train_set has two lag values, then 
    x = today
    y = tomorrow
    
    by predicting x for y (see rmse below) we assume that what happened in the previous time step will be the same
    as what will happen in the next time step
    """
    predictions = test_x

    # calc rmse
    rmse = sqrt(mean_squared_error(test_y, test_x))

    print('Test RMSE: %.3f' % rmse)

    if show_explanation:
        print("Consider: "
              "* the model should be one-step behind reality"
              "* a REAL predicted model should be stationary, however,"
              "this model won't be (provided the input data isn't either)"
              "* use Augmented Dickey-Fuller test to check for stationarity"
              )

    if viz == 'test+predict':
        sns.set(rc={'figure.figsize': (18, 6)})
        sns.lineplot(data=test_y, color='green', label='test_y')
        sns.lineplot(data=predictions, color='red', label='predictions')
    if viz == 'all':
        sns.set(rc={'figure.figsize': (18, 6)})
        sns.lineplot(data=train_y, color='blue', label='train_y')
        sns.lineplot(data=predictions, color='red', label='predictions')
        sns.lineplot(data=test_y, color='green', label='test_y')

    residuals = pd.DataFrame(test_y.to_numpy() - predictions.to_numpy())
    return train_x, train_y, test_x, test_y, predictions, rmse, residuals
