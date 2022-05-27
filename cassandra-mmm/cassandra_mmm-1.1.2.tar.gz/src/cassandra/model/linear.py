from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from cassandra.data.trasformations.trasformations import create_model
from cassandra.model.modelEvaluation.plot import show_nrmse, show_mape, show_rsquared, show_rssd
import numpy as np


def linear(df, X_columns, target, name_model, medias=[], organic=[], metric=None,
           return_metric=False, size=0.2, positive=False, random_state=42, force_coeffs=False, coeffs=[], intercept=0):
    if metric is None:
        metric = ['rsq_train', 'rsq_test', 'nrmse_train', 'nrmse_test', 'mape_train', 'mape_test', 'rssd']

    X = df[X_columns]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=size, random_state=random_state)

    if medias or organic:
        model = create_model(medias, organic, LinearRegression(positive=positive))
    else:
        model = LinearRegression(positive=positive)

    model.fit(X_train, y_train)

    if force_coeffs:
        model.intercept_ = intercept
        if coeffs:
            model.coef_ = np.array(coeffs)

    # Ask the model to predict on X_test without having Y_test
    # This will give you exact predicted values

    # We can use our NRMSE and MAPE functions as well

    # Create new DF not to edit the original one
    result = df

    # Create a new column with predicted values
    if medias or organic:
        result['prediction'] = model.predict(result)
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)
    else:
        result['prediction'] = model.predict(X)
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

    #metrics_values = choose_metric(name_model, metric, return_metric, y_train, y_test, y_train_pred, y_test_pred)
    metrics_values = {}

    # Score returns the accuracy of the above prediction or R^2
    if 'rsq_train' in metric:
        try:
            rsq_train = show_rsquared(np.array(y_train), np.array(y_train_pred))
        except:
            rsq_train = -100
        if return_metric:
            metrics_values[name_model + '_rsq_train'] = rsq_train
        print(name_model, 'RSQ train: ', rsq_train)

    if 'rsq_test' in metric:
        try:
            rsq_test = show_rsquared(np.array(y_test), np.array(y_test_pred))
        except:
            rsq_test = -100
        if return_metric:
            metrics_values[name_model + '_rsq_test'] = rsq_test
        print(name_model, 'RSQ test: ', rsq_test)

    # Get the NRMSE values
    if 'nrmse_train' in metric:
        try:
            nrmse_train_val = show_nrmse(np.array(y_train), np.array(y_train_pred))
        except:
            nrmse_train_val = 100
        if return_metric:
            metrics_values[name_model + '_nrmse_train'] = nrmse_train_val
        print(name_model, 'NRMSE train: ', nrmse_train_val)

    if 'nrmse_test' in metric:
        try:
            nrmse_test_val = show_nrmse(np.array(y_test), np.array(y_test_pred))
        except:
            nrmse_test_val = 100
        if return_metric:
            metrics_values[name_model + '_nrmse_test'] = nrmse_test_val
        print(name_model, 'NRMSE test: ', nrmse_test_val)

    # Get the MAPE values
    if 'mape_train' in metric:
        try:
            mape_train_val = show_mape(np.array(y_train), np.array(y_train_pred))
        except:
            mape_train_val = 100
        if return_metric:
            metrics_values[name_model + '_mape_train'] = mape_train_val
        print(name_model, 'MAPE train: ', mape_train_val)

    if 'mape_test' in metric:
        try:
            mape_test_val = show_mape(np.array(y_test), np.array(y_test_pred))
        except:
            mape_test_val = 100
        if return_metric:
            metrics_values[name_model + '_mape_test'] = mape_test_val
        print(name_model, 'MAPE test: ', mape_test_val)

    if 'rssd' in metric:
        try:
            rssd_val = show_rssd(X, model.coef_)
        except:
            rssd_val = 100
        if return_metric:
            metrics_values[name_model + '_rssd'] = rssd_val
        print(name_model, 'RSSD: ', rssd_val)

    if metrics_values:
        return result, model, metrics_values
    else:
        return result, model


# def choose_metric(name_model, metric, return_metric, y_train, y_test, y_train_pred, y_test_pred):
#     metrics_values = {}
#
#     # Score returns the accuracy of the above prediction or R^2
#     if 'rsq_train' in metric:
#         try:
#             rsq_train = show_rsquared(np.array(y_train), np.array(y_train_pred))
#         except:
#             rsq_train = -100
#         if return_metric:
#             metrics_values[name_model + '_rsq_train'] = rsq_train
#         print(name_model, 'RSQ train: ', rsq_train)
#
#     if 'rsq_test' in metric:
#         try:
#             rsq_test = show_rsquared(np.array(y_test), np.array(y_test_pred))
#         except:
#             rsq_test = -100
#         if return_metric:
#             metrics_values[name_model + '_rsq_test'] = rsq_test
#         print(name_model, 'RSQ test: ', rsq_test)
#
#     # Get the NRMSE values
#     if 'nrmse_train' in metric:
#         try:
#             nrmse_train_val = show_nrmse(np.array(y_train), np.array(y_train_pred))
#         except:
#             nrmse_train_val = 100
#         if return_metric:
#             metrics_values[name_model + '_nrmse_train'] = nrmse_train_val
#         print(name_model, 'NRMSE train: ', nrmse_train_val)
#
#     if 'nrmse_test' in metric:
#         try:
#             nrmse_test_val = show_nrmse(np.array(y_test), np.array(y_test_pred))
#         except:
#             nrmse_test_val = 100
#         if return_metric:
#             metrics_values[name_model + '_nrmse_test'] = nrmse_test_val
#         print(name_model, 'NRMSE test: ', nrmse_test_val)
#
#     # Get the MAPE values
#     if 'mape_train' in metric:
#         try:
#             mape_train_val = show_mape(np.array(y_train), np.array(y_train_pred))
#         except:
#             mape_train_val = 100
#         if return_metric:
#             metrics_values[name_model + '_mape_train'] = mape_train_val
#         print(name_model, 'MAPE train: ', mape_train_val)
#
#     if 'mape_test' in metric:
#         try:
#             mape_test_val = show_mape(np.array(y_test), np.array(y_test_pred))
#         except:
#             mape_test_val = 100
#         if return_metric:
#             metrics_values[name_model + '_mape_test'] = mape_test_val
#         print(name_model, 'MAPE test: ', mape_test_val)
#
#     return metrics_values
