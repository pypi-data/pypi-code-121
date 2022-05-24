from cryptotoolbox.mixing import mixing_utility

import lightgbm as lgb

import numpy as np

import pmdarima as pm

from statsmodels.tsa.stattools import adfuller

import pandas as pd

def recursive_adf(serie_A, order, alpha, verbose = False):
  try:
    assert serie_A.isna().sum() == 0
  except AssertionError:
    serie_A = serie_A.fillna(0)
  adA = adfuller(serie_A, maxlag=None, regression ='c', autolag = 'AIC')
  if adA[1] < alpha:
    if verbose:
      print('ADF:: Diff for serie', serie_A.name, ':', order)
  else:
    order = order+1
    recursive_adf(serie_A.diff(), order = order, alpha = alpha)
  return order

def auto_arima(train_data, test_data, return_reg_metrics=False):
    train = train_data.astype(float)
    test = test_data.astype(float)
    if recursive_adf(pd.Series(train_data), 0, .05) == 0:
        wst = True
    else:
        wst = False
    model = pm.auto_arima(train, seaonality=False, maxiter=200, information_criterion='aicc',
                          error_action="ignore", suppress_warnings=True, with_intercept=True, stepwise=True,
                          stationary=wst, start_p=0, start_q=0)
    forecasts = model.predict(len(test))
    x = pd.Series(np.concatenate([train, forecasts])).astype(float)
    if not return_reg_metrics:
        return forecasts
    else:
        from sklearn.metrics import mean_squared_error
        from sklearn.metrics import r2_score
        from sklearn.metrics import max_error
        rmse = np.sqrt(mean_squared_error(test, forecasts))
        max_err = max_error(test, forecasts)
        return forecasts, rmse, max_err

class ArimaModel():

    def __init__(self):
        self.model = None

    def calibrate(self, X, y):
        return

    def fit(self, X_train, y_train, X_val, y_val):#, method = 'standard'):
        if recursive_adf(pd.Series(y_train), 0, .05) == 0:
            wst = True
        else:
            wst = False
        self.model = pm.auto_arima(y_train, seaonality=False, maxiter=200, information_criterion='aicc',
                              error_action="ignore", suppress_warnings=True, with_intercept=True, stepwise=True,
                              stationary=wst, start_p=0, start_q=0)


    def predict(self, X_test):
        y_pred = self.model.predict(len(X_test))
        return y_pred

    def get_features_importance(self, features_names):#, method = 'standard'):
        return
