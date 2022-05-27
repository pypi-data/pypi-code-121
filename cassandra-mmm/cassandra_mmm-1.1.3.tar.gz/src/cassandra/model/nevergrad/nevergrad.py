import nevergrad as ng
from cassandra.model.nevergrad.utils import instrum_transformations_nevergrad, create_df_transformations_nevergrad, \
    choose_optimizer_algoritm, optimize_metric
from cassandra.model.utils import choose_model


def nevergrad_model(df, hyperparameters_dict, medias, others, target, use_intercept=True, use_adstock=True,
                    use_saturation=True,
                    adstock_type='weibull', saturation_type='hill', model_regression='linear',
                    X_transformations_columns=[],
                    model_regression_log_log='linear', ridge_number=0, metric=None,
                    return_metric=True, size=0.2, positive=False, random_state=42, metric_return=[],
                    force_coeffs=True, coeffs=[], intercept=0, optimizer_algoritm='TwoPointsDE', budget=1000,
                    num_workers=1):
    if metric is None:
        metric = ['rsq_train', 'rsq_test', 'nrmse_train', 'nrmse_test', 'mape_train', 'mape_test', 'rssd']

    value_trasf = instrum_transformations_nevergrad(hyperparameters_dict)

    metric_array = []
    df_transformations = df.copy()
    metrics_values = {}
    all_hyper = list(hyperparameters_dict.keys())

    def build_model(**all_hyper):
        df_transf = create_df_transformations_nevergrad(all_hyper, df, df_transformations, medias, use_adstock,
                                                        use_saturation, adstock_type, saturation_type)

        all_features = medias + others

        # CHECK
        if 'ridge_number' in all_hyper:
            nonlocal ridge_number
            ridge_number = all_hyper['ridge_number']

        if model_regression == 'logLog':
            all_features = [x for x in all_features if x not in X_transformations_columns]

        if force_coeffs:
            nonlocal coeffs
            nonlocal intercept
            if model_regression == 'logLog':
                all_features_coeffs = [value for key, value in all_hyper.items() if '_spend_' not in key if
                                       'ridge' not in key if key not in X_transformations_columns if
                                       'intercept' not in key]
                X_transformations_columns_coeffs = [value for key, value in all_hyper.items() if '_spend_' not in key if
                                                    'ridge' not in key if key not in all_features if
                                                    'intercept' not in key]
                if use_intercept:
                    intercept = [value for key, value in all_hyper.items() if 'intercept' in key]
                coeffs = X_transformations_columns_coeffs + all_features_coeffs
            else:
                all_coeffs = [value for key, value in all_hyper.items() if '_spend_' not in key if 'ridge' not in key]

                coeffs = all_coeffs[:-1]
                if use_intercept:
                    intercept = all_coeffs[-1]

        result, model, metrics_values = choose_model(df_transf, all_features, target, model_regression,
                                                     X_transformations_columns,
                                                     model_regression_log_log, ridge_number, metric,
                                                     return_metric, size, positive, random_state, force_coeffs,
                                                     coeffs, intercept)

        metric_to_optimize = optimize_metric(metric_return, metrics_values)
        metric_array.append(metric_to_optimize)

        return metric_to_optimize, result, model, metrics_values

    def build_model_result(**all_hyper):

        metric_to_optimize, result, model, metrics_values = build_model(**all_hyper)

        return metric_to_optimize

    instrum = ng.p.Instrumentation(**value_trasf)
    optimizer = choose_optimizer_algoritm(optimizer_algoritm, budget, num_workers, instrum)
    recommendation = optimizer.minimize(build_model_result)

    if len(metric_return) == 1:
        recom = recommendation.value[1]
        metric, result, model, metrics_values = build_model(**recom)

        return metrics_values, result, model, recom, metric_array
    else:
        if optimizer.pareto_front():
            recom = [col.value[1] for col in optimizer.pareto_front()]
        else:
            recom = optimizer.recommend().value[1]

        result_mult, model_mult, metrics_values_mult = [], [], []
        for r in recom:
            metric_only, result_only, model_only, metrics_values_only = build_model(**r)
            result_mult.append(result_only)
            model_mult.append(model_only)
            metrics_values_mult.append(metrics_values_only)

        return metrics_values_mult, result_mult, model_mult, recom, metric_array
