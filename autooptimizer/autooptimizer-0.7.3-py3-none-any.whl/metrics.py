import numpy as np

def root_mean_squared_error(y_true, y_pred):
    rmse = np.sqrt(np.square(np.subtract(y_true, y_pred)).mean())
    return rmse
    
def root_mean_squared_log_error(y_true, y_pred):
    rmsle = np.sqrt(np.square(np.subtract(np.log(y_pred + 1), np.log(y_true + 1))).mean())
    return rmsle

def root_mean_squared_precentage_error(y_true, y_pred):
    rmspe = (np.sqrt(np.mean(np.square(np.subtract(y_true, y_pred) / y_true)))) * 100
    return rmspe

def symmetric_mean_absolute_precentage_error(y_true, y_pred):
    smape = 100/len(y_true) * np.sum(2 * np.abs(np.subtract(y_pred, y_true)) / (np.abs(y_true) + np.abs(y_pred)))
    return smape
    
def mean_bias_error(y_true, y_pred):
    mbe = np.mean(np.subtract(y_pred, y_true))
    return mbe

def relative_squared_error(y_true, y_pred): 
    rse = np.sum(np.square(np.subtract(y_true, y_pred))) / np.sum(np.square(np.subtract(np.average(y_true), y_true)))
    return rse

def root_relative_squared_error(y_true, y_pred):
    rrse = np.sqrt(np.sum(np.square(np.subtract(y_true, y_pred))) / np.sum(np.square(np.subtract(np.average(y_true), y_true))))
    return rrse
    
def relative_absolute_error(y_true, y_pred):
    rae = np.sum(np.abs(np.subtract(y_true, y_pred))) / (np.sum(np.abs(np.subtract(y_true, np.average(y_true)))) + 1e-10)
    return rae

def median_absolute_percentage_error(y_true, y_pred):
    mape = np.median((np.abs(np.subtract(y_true, y_pred)/ y_true)) ) * 100
    return mape

def mean_absolute_percentage_error(y_true, y_pred):
    mape = np.mean((np.abs(np.subtract(y_true, y_pred)/ y_true))) * 100
    return mape
