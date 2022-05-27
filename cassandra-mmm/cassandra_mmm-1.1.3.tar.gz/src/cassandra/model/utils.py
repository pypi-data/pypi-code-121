from cassandra.model.linear import linear
from cassandra.model.logLinear import logLinear
from cassandra.model.ridge import ridge
from cassandra.model.logLog import logLog


def choose_model(df, X_columns, y_column, model_regression='linear', X_trasformations_columns=[],
                 model_regression_log_log='linear', ridge_number=0, metric=None,
                 return_metric=False, size=0.2, positive=False, random_state=42, force_coeffs=False, coeffs=[],
                 intercept=0):
    if metric is None:
        metric = ['rsq_train', 'rsq_test', 'nrmse_train', 'nrmse_test', 'mape_train', 'mape_test']
    metrics_values = {}

    if 'linear' in model_regression:
        if return_metric:
            result, model, metrics_values = linear(df, X_columns, y_column, model_regression, metric=metric,
                                                   return_metric=return_metric, size=size, positive=positive,
                                                   random_state=random_state, force_coeffs=force_coeffs, coeffs=coeffs,
                                                   intercept=intercept)
        else:
            result, model = linear(df, X_columns, y_column, model_regression, metric=metric,
                                   return_metric=return_metric,
                                   size=size, positive=positive, random_state=random_state, force_coeffs=force_coeffs,
                                   coeffs=coeffs, intercept=intercept)

    elif 'logLinear' in model_regression:
        if return_metric:
            result, model, metrics_values = logLinear(df, X_columns, y_column, model_regression, metric=metric,
                                                      return_metric=return_metric, size=size, positive=positive,
                                                      random_state=random_state, force_coeffs=force_coeffs,
                                                      coeffs=coeffs, intercept=intercept)
        else:
            result, model = logLinear(df, X_columns, y_column, model_regression, metric=metric,
                                      return_metric=return_metric,
                                      size=size, positive=positive, random_state=random_state,
                                      force_coeffs=force_coeffs, coeffs=coeffs, intercept=intercept)

    elif 'logLog' in model_regression:
        if return_metric:
            result, model, metrics_values = logLog(df, X_trasformations_columns, X_columns, y_column, model_regression,
                                                   model_regression=model_regression_log_log, metric=metric,
                                                   return_metric=return_metric, size=size, positive=positive,
                                                   random_state=random_state, force_coeffs=force_coeffs, coeffs=coeffs,
                                                   intercept=intercept)
        else:
            result, model = logLog(df, X_trasformations_columns, X_columns, y_column, model_regression,
                                   model_regression=model_regression_log_log, metric=metric,
                                   return_metric=return_metric, size=size, positive=positive, random_state=random_state,
                                   force_coeffs=force_coeffs, coeffs=coeffs, intercept=intercept)

    elif 'ridge' in model_regression:
        if return_metric:
            result, model, metrics_values = ridge(df, X_columns, y_column, model_regression, ridge_number=ridge_number,
                                                  metric=metric,
                                                  return_metric=return_metric, size=size, positive=positive,
                                                  random_state=random_state, force_coeffs=force_coeffs, coeffs=coeffs,
                                                  intercept=intercept)
        else:
            result, model = ridge(df, X_columns, y_column, model_regression, ridge_number=ridge_number, metric=metric,
                                  return_metric=return_metric, size=size, positive=positive, random_state=random_state,
                                  force_coeffs=force_coeffs, coeffs=coeffs, intercept=intercept)

    if metrics_values:
        return result, model, metrics_values
    else:
        return result, model
