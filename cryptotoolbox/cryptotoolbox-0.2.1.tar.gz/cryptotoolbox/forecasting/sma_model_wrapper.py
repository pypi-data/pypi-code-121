import numpy as np
import scipy
import pandas as pd
from scipy.stats import linregress


def interpolate_nans(X, type_='linear'):
  # arr = interpolate_nans(arr.reshape(-1,1), type_ = 'linear')
  if type_ == 'linear':
    for j in range(X.shape[1]):
      mask_j = np.isnan(X[:, j])
      X[mask_j, j] = np.interp(np.flatnonzero(mask_j), np.flatnonzero(~mask_j), X[~mask_j, j])
  elif type_ == 'cubic':
    from scipy.interpolate import CubicSpline
    for j in range(X.shape[1]):
      mask_j = np.isnan(X[:, j])
      c = CubicSpline(np.flatnonzero(~mask_j), X[~mask_j, j], axis=0, bc_type='not-a-knot')
      X[mask_j, j] = c(np.flatnonzero(mask_j))
  elif type_ == 'poly':
    from scipy.interpolate import BarycentricInterpolator
    for j in range(X.shape[1]):
      mask_j = np.isnan(X[:, j])
      c = scipy.interpolate.BarycentricInterpolator(np.flatnonzero(~mask_j), X[~mask_j, j])
      X[mask_j, j] = c(np.flatnonzero(mask_j))
  return X

def SMA_predict(train_data, test_data, fit_on_last = 10, interp_type = 'linear', return_reg_metrics = False):
  if not isinstance(train_data, np.ndarray):
    train = train_data.values.astype(float)
  else:
    train = train_data.astype(float)
  if not isinstance(test_data, np.ndarray):
    test = test_data.values.astype(float)
  else:
    test = test_data.astype(float)
  assert pd.Series(train).isna().sum().sum() == 0, 'nans found in your input.'
  slope, intercept, rvalue, pvalue, stder = linregress(np.arange(0,fit_on_last), train[-fit_on_last:])
  p = intercept + slope*(len(test))
  arr = np.concatenate((train, np.zeros(shape = (len(test)-1,))))
  arr = np.concatenate((arr, np.array([p])))
  arr[arr == 0] = np.nan
  arr = arr[-(fit_on_last+(len(test))):].copy()
  arr = interpolate_nans(arr.reshape(-1,1), type_= interp_type)
  fcst = arr[-(len(test)):].ravel()
  if not return_reg_metrics:
    return fcst
  else:
    from sklearn.metrics import mean_squared_error
    from sklearn.metrics import max_error
    rmse = np.sqrt(mean_squared_error(test,fcst))
    max_err = max_error(test, fcst)
    return fcst,rmse, max_err


class SmaModel():

    def __init__(self, fit_on_last = 5, interp_type = 'linear'):
        self.model = None
        self.fit_on_last = fit_on_last
        self.interp_type = interp_type

    def calibrate(self, X, y):
        return

    def fit(self, X_train, y_train, X_val, y_val):
        self.model = y_train
        return

    def predict(self, X_test):
        slope, intercept, rvalue, pvalue, stder = linregress(np.arange(0, self.fit_on_last), self.model[-self.fit_on_last:])
        p = intercept + slope * (len(X_test))
        arr = np.concatenate((self.model, np.zeros(shape=(len(X_test) - 1,))))
        arr = np.concatenate((arr, np.array([p])))
        arr[arr == 0] = np.nan
        arr = arr[-(self.fit_on_last + (len(X_test))):].copy()
        arr = interpolate_nans(arr.reshape(-1, 1), type_=self.interp_type)
        y_pred = arr[-(len(X_test)):].ravel()
        return y_pred

    def get_features_importance(self, features_names):
        return
