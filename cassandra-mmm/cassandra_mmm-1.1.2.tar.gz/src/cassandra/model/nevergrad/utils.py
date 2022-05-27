from cassandra.data.trasformations.trasformations import adstock_weibull, saturation, saturation_hill, adstock_geometric
import nevergrad as ng
import numpy as np


def create_df_transformations_nevergrad(trasf, df, df_transformations, medias, use_adstock=True, use_saturation=True,
                                        adstock_type='weibull', saturation_type='hill'):
    if use_saturation:
        if saturation_type == 'hill':
            if use_adstock:
                if adstock_type == 'weibull':
                    for m in medias:
                        df_transformations[m] = saturation_hill(
                            adstock_weibull(df[m], trasf[m + '_scale'], trasf[m + '_shape']).replace([np.inf, -np.inf],
                                                                                                     0),
                            trasf[m + '_alpha'], trasf[m + '_gamma'])

                elif adstock_type == 'geometric':
                    for m in medias:
                        df_transformations[m] = saturation_hill(adstock_geometric(df[m], trasf[m + '_theta']),
                                                                trasf[m + '_alpha'], trasf[m + '_gamma'])
            else:
                for m in medias:
                    df_transformations[m] = saturation_hill(df[m], trasf[m + '_alpha'], trasf[m + '_gamma'])

        else:
            if use_adstock:
                if adstock_type == 'weibull':
                    for m in medias:
                        df_transformations[m] = saturation(
                            adstock_weibull(df[m], trasf[m + '_scale'], trasf[m + '_shape']).replace([np.inf, -np.inf],
                                                                                                     0),
                            trasf[m + '_beta'])

                elif adstock_type == 'geometric':
                    for m in medias:
                        df_transformations[m] = saturation(adstock_geometric(df[m], trasf[m + '_theta']), trasf[m + '_beta'])
            else:
                for m in medias:
                    df_transformations[m] = saturation(df[m], trasf[m + '_beta'])

    else:
        if use_adstock:
            if adstock_type == 'weibull':
                for m in medias:
                    df_transformations[m] = adstock_weibull(df[m], trasf[m + '_scale'], trasf[m + '_shape']).replace(
                        [np.inf, -np.inf], 0)

            elif adstock_type == 'geometric':
                for m in medias:
                    df_transformations[m] = adstock_geometric(df[m], trasf[m + '_theta'])

    return df_transformations


def instrum_variables_nevergrad(medias, organic, force_coeffs=False, use_intercept=True, use_adstock=True,
                                use_saturation=True, saturation_type='hill', adstock_type='weibull'):
    result_dict = {}

    if force_coeffs:
        for x in medias:
            result_dict[x] = {'lower': 0, 'upper': None}
        for x in organic:
            if '_org' in x:
                result_dict[x] = {'lower': 0, 'upper': None}
            else:
                result_dict[x] = {'lower': None, 'upper': None}
        if use_intercept:
            result_dict['intercept'] = {'lower': None, 'upper': None}

    if use_adstock:
        if adstock_type == 'weibull':
            for x in medias:
                result_dict[x + '_shape'] = {'lower': 0.0001, 'upper': 10}
                result_dict[x + '_scale'] = {'lower': 0, 'upper': 0.1}

                if use_saturation:
                    if saturation_type == 'hill':
                        result_dict[x + '_alpha'] = {'lower': 0.5, 'upper': 3}
                        result_dict[x + '_gamma'] = {'lower': 0.3, 'upper': 1}
                    else:
                        result_dict[x + '_beta'] = {'lower': 0.5, 'upper': 3}

        elif adstock_type == 'geometric':
            for x in medias:
                result_dict[x + '_theta'] = {'lower': 0, 'upper': 0.3}

                if use_saturation:
                    if saturation_type == 'hill':
                        result_dict[x + '_alpha'] = {'lower': 0.5, 'upper': 3}
                        result_dict[x + '_gamma'] = {'lower': 0.3, 'upper': 1}
                    else:
                        result_dict[x + '_beta'] = {'lower': 0.5, 'upper': 3}

    return result_dict


def instrum_transformations_nevergrad(hyperparameters_dict):
    result = {}
    for key, value in hyperparameters_dict.items():
        result[key] = ng.p.Scalar(lower=hyperparameters_dict[key]['lower'], upper=hyperparameters_dict[key]['upper'])

    return result


# All algorithms have strengths and weaknesses. Questionable rules of thumb could be: @NGOpt is “meta”-optimizer which
# adapts to the provided settings (budget, number of workers, parametrization) and should therefore be a good
# default. @TwoPointsDE is excellent in many cases, including very high num_workers. @PortfolioDiscreteOnePlusOne is
# excellent in discrete settings of mixed settings when high precision on parameters is not relevant; it’s possibly a
# good choice for hyperparameter choice. @OnePlusOne is a simple robust method for continuous parameters with
# num_workers < 8. @CMA is excellent for control (e.g. neurocontrol) when the environment is not very noisy (
# num_workers ~50 ok) and when the budget is large (e.g. 1000 x the dimension). @TBPSA is excellent for problems
# corrupted by noise, in particular overparameterized (neural) ones; very high num_workers ok). @PSO is excellent in
# terms of robustness, high num_workers ok. @ScrHammersleySearchPlusMiddlePoint is excellent for super parallel cases
# (fully one-shot, i.e. num_workers = budget included) or for very multimodal cases (such as some of our MLDA
# problems); don’t use softmax with this optimizer. @RandomSearch is the classical random search baseline; don’t use
# softmax with this optimizer.
def choose_optimizer_algoritm(optimizer_algoritm, budget, num_workers, instrum):
    if optimizer_algoritm == 'TwoPointsDE':
        optimizer = ng.optimizers.TwoPointsDE(parametrization=instrum, budget=budget, num_workers=num_workers)
    if optimizer_algoritm == 'NGOpt':
        optimizer = ng.optimizers.NGOpt(parametrization=instrum, budget=budget, num_workers=num_workers)
    if optimizer_algoritm == 'PortfolioDiscreteOnePlusOne':
        optimizer = ng.optimizers.PortfolioDiscreteOnePlusOne(parametrization=instrum, budget=budget,
                                                              num_workers=num_workers)
    if optimizer_algoritm == 'OnePlusOne':
        optimizer = ng.optimizers.OnePlusOne(parametrization=instrum, budget=budget, num_workers=num_workers)
    if optimizer_algoritm == 'CMA':
        optimizer = ng.optimizers.CMA(parametrization=instrum, budget=budget, num_workers=num_workers)
    if optimizer_algoritm == 'TBPSA':
        optimizer = ng.optimizers.TBPSA(parametrization=instrum, budget=budget, num_workers=num_workers)
    if optimizer_algoritm == 'PSO':
        optimizer = ng.optimizers.PSO(parametrization=instrum, budget=budget, num_workers=num_workers)
    if optimizer_algoritm == 'ScrHammersleySearchPlusMiddlePoint':
        optimizer = ng.optimizers.ScrHammersleySearchPlusMiddlePoint(parametrization=instrum, budget=budget,
                                                                     num_workers=num_workers)
    if optimizer_algoritm == 'RandomSearch':
        optimizer = ng.optimizers.RandomSearch(parametrization=instrum, budget=budget, num_workers=num_workers)

    return optimizer


def optimize_metric(metric_return, metrics_values):
    result = []
    for key, value in metrics_values.items():
        for m in metric_return:
            if m in key:
                if 'rsq' in metric_return:
                    result.append(-value)
                else:
                    result.append(value)
    return result
