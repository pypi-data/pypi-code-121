from cassandra.model.utils import choose_model


def nestedModel(df, X_columns, y_column, model_regression='linear', X_trasformations_columns=[],
                model_regression_log_log='linear', ridge_number=0, metric=None,
                return_metric=False, size=0.2, positive=False, random_state=42, force_coeffs=False, coeffs=[],
                intercept=0):
    if metric is None:
        metric = ['rsq_train', 'rsq_test', 'nrmse_train', 'nrmse_test', 'mape_train', 'mape_test', 'rssd']
    metrics_values = {}

    if return_metric:
        result, model, metrics_values = choose_model(df, X_columns, y_column, model_regression,
                                                     X_trasformations_columns,
                                                     model_regression_log_log, ridge_number, metric,
                                                     return_metric, size, positive, random_state, force_coeffs, coeffs,
                                                     intercept)
    else:
        result, model = choose_model(df, X_columns, y_column, model_regression, X_trasformations_columns,
                                     model_regression_log_log, ridge_number, metric,
                                     return_metric, size, positive, random_state, force_coeffs, coeffs, intercept)

    if metrics_values:
        return result, model, metrics_values
    else:
        return result, model


def mainNestedModel(sub_df, sub_X_columns, sub_y_column, X_columns, y_column, sub_model_regression='linear',
                    sub_X_trasformations_columns=[],
                    sub_model_regression_log_log='linear', sub_ridge_number=0, sub_metric=None,
                    return_sub_metric=False, sub_size=0.2, sub_positive=False, sub_random_state=42,
                    sub_force_coeffs=False, sub_coeffs=[], sub_intercept=0, model_regression='linear',
                    X_trasformations_columns=[], model_regression_log_log='linear', ridge_number=0,
                    metric=None, return_metric=False, size=0.2, positive=False, random_state=42,
                    force_coeffs=False, coeffs=[], intercept=0):
    if metric is None:
        sub_metric = ['rsq_train', 'rsq_test', 'nrmse_train', 'nrmse_test', 'mape_train', 'mape_test', 'rssd']
    if metric is None:
        metric = ['rsq_train', 'rsq_test', 'nrmse_train', 'nrmse_test', 'mape_train', 'mape_test', 'rssd']
    sub_metric_values = {}
    metrics_values = {}
    if return_sub_metric:
        sub_result, sub_model, sub_metric_values = nestedModel(sub_df, sub_X_columns, sub_y_column,
                                                               sub_model_regression, sub_X_trasformations_columns,
                                                               sub_model_regression_log_log, sub_ridge_number,
                                                               sub_metric, return_sub_metric, size=sub_size,
                                                               positive=sub_positive, random_state=sub_random_state,
                                                               force_coeffs=sub_force_coeffs, coeffs=sub_coeffs,
                                                               intercept=sub_intercept)
    else:
        sub_result, sub_model = nestedModel(sub_df, sub_X_columns, sub_y_column, sub_model_regression,
                                            sub_X_trasformations_columns,
                                            sub_model_regression_log_log, sub_ridge_number, sub_metric, size=sub_size,
                                            positive=sub_positive, random_state=sub_random_state,
                                            force_coeffs=sub_force_coeffs, coeffs=sub_coeffs,
                                            intercept=sub_intercept)

    df = sub_result.copy()

    df[sub_y_column] = sub_result['prediction'].copy()

    if return_metric:
        result, model, metrics_values = choose_model(df, X_columns, y_column, model_regression,
                                                     X_trasformations_columns,
                                                     model_regression_log_log, ridge_number, metric,
                                                     return_metric, size, positive, random_state, force_coeffs, coeffs,
                                                     intercept)
    else:
        result, model = choose_model(df, X_columns, y_column, model_regression, X_trasformations_columns,
                                     model_regression_log_log, ridge_number, metric,
                                     return_metric, size, positive, random_state, force_coeffs, coeffs, intercept)

    if metrics_values:
        return result, model, metrics_values, sub_result, sub_model, sub_metric_values
    else:
        return result, model, sub_result, sub_model
