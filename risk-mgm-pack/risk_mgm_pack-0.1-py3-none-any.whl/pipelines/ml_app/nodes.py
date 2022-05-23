import pandas as pd
import logging

import numpy as np

from moosir_feature.model_validations.basic_parameter_searcher import ParameterSearcher
from moosir_feature.model_validations.benchmarking import run_benchmarking  # , NaiveModel #, RandomModel
from moosir_feature.model_validations.model_validator import CustomTsCv
from moosir_feature.transformers.feature_cleaning.feature_cleaner import timestamp_ohlc_resample
from moosir_feature.transformers.features_common.calculator import align_features_and_targets, combine_features
from moosir_feature.transformers.managers.feature_manager import FeatureCreatorManager
from moosir_feature.model_validations.model_cv_runner import predict_on_cv
from moosir_feature.trades.alpha_manager import create_quantile_alphas, create_absolute_prediction_alphas

from moosir_feature.transformers.managers.settings import IndicatorTargetSettings, \
    SignalFeatureSettings, TargetSettings, IndicatorLagSettings, IndicatorFeatureSettings

# from sklearn.dummy import DummyRegressor
from ..domain.risk_management import *

log = logging.getLogger(__name__)


def create_random_alpha(ohlc: pd.DataFrame):
    alphas = timestamp_ohlc_resample(ohlc=ohlc, resample_freq="5T")
    sample_n = len(alphas)
    alphas["Signal"] = np.random.randint(low=-1, high=2, size=sample_n)
    # alphas = alphas[["Signal"]]
    return dict(alphas=alphas)


def create_features_targets(instances: pd.DataFrame,
                            model_alphas: pd.DataFrame,
                            target_ind_params: dict,
                            feature_ind_params: dict,
                            lag_ind_params: dict
                            ):
    target_settings = IndicatorTargetSettings(**target_ind_params)
    # todo: not using params, remove it
    # feature_ind_settings = [IndicatorFeatureSettings(**feature_ind_params)]
    feature_ind_settings = []
    lag_ind_settings = [IndicatorLagSettings(**lag_ind_params)]

    fc_mgr = FeatureCreatorManager(target_settings=target_settings,
                                   feature_settings_list=feature_ind_settings,
                                   lag_settings_list=lag_ind_settings)
    instance_features, instance_targets, _ = fc_mgr.create_features_and_targets(instances=instances)

    # todo: bug in signal, it removes the index name!!!
    instance_features.index.name = "Timestamp"

    # todo: move it to package, wrong here
    features = instance_features
    targets = instance_targets
    # alphas = model_alphas[model_alphas["Signal"] != 0][["Signal"]]
    # alphas = model_alphas["Signal"]
    # alphas.columns = ["Signal_Input"]
    # features = combine_features([instance_features, alphas])
    # features, targets, _ = align_features_and_targets(features=features, targets=instance_targets)

    features, targets, _ = select_windows(features=features, targets=targets)

    return dict(features=features, targets=targets)


def run_cross_validation(features: pd.DataFrame,
                         targets: pd.DataFrame,
                         cv_search_params: dict,
                         search_params: dict,
                         metrics: list
                         ):
    log.info("searching parameters and running cross validation")

    searcher = ParameterSearcher()

    estimator = LinearVarModel(feature_cols=[], kernel=3)

    search_result = searcher.run_parameter_search_multiple_cvs(X=features,
                                                               y=targets,
                                                               estimator=estimator,
                                                               cv_params=cv_search_params,
                                                               param_grid=search_params,
                                                               metrics=metrics,
                                                               )

    return dict(search_result=search_result)


def benchmark_best_model(features: pd.DataFrame,
                         targets: pd.DataFrame,
                         best_params: dict,
                         benchmark_cv_params: dict,
                         metrics: list
                         ):
    best_model = LinearVarModel(**best_params)
    models = [NaiveModel(targets=targets.copy(), look_back_len=12), best_model]

    cv = CustomTsCv(train_n=benchmark_cv_params["train_length"],
                    test_n=benchmark_cv_params["test_length"],
                    sample_n=len(features),
                    train_shuffle_block_size=benchmark_cv_params["train_shuffle_block_size"])

    benchmark_result = run_benchmarking(models=models, targets=targets, features=features, cv=cv, metrics=metrics)

    return dict(benchmark_result=benchmark_result)


def train_predict_best_params(instances: pd.DataFrame,
                              target_ind_params: dict,
                              feature_ind_params: dict,
                              lag_ind_params: dict,
                              best_params: dict,
                              benchmark_cv_params: dict):
    target_settings = IndicatorTargetSettings(**target_ind_params)
    feature_ind_settings = []
    lag_ind_settings = [IndicatorLagSettings(**lag_ind_params)]

    fc_mgr = FeatureCreatorManager(target_settings=target_settings,
                                   feature_settings_list=feature_ind_settings,
                                   lag_settings_list=lag_ind_settings)

    features, targets, _ = fc_mgr.create_features_and_targets(instances=instances)

    features, targets, _ = select_windows(features=features, targets=targets)

    best_model = LinearVarModel(**best_params)
    cv = CustomTsCv(train_n=benchmark_cv_params["train_length"],
                    test_n=benchmark_cv_params["test_length"],
                    sample_n=len(features),
                    train_shuffle_block_size=None)

    prediction_result = predict_on_cv(model=best_model, features=features, targets=targets, cv=cv)

    return dict(prediction_result=prediction_result)


def create_alpha(instances: pd.DataFrame, prediction_result: pd.DataFrame):
    alphas = create_absolute_prediction_alphas(instances=instances, prediction_result=prediction_result)

    log.info(alphas)
    log.info(alphas.describe())

    return dict(alphas=alphas)


def train_best_model_to_deploy(instances: pd.DataFrame,
                               target_ind_params: dict,
                               feature_ind_params: dict,
                               lag_ind_params: dict,
                               best_params,
                               final_train_len: int):
    instances = instances.iloc[-final_train_len:]

    target_settings = IndicatorTargetSettings(**target_ind_params)
    feature_ind_settings = []
    lag_ind_settings = [IndicatorLagSettings(**lag_ind_params)]

    fc_mgr = FeatureCreatorManager(target_settings=target_settings,
                                   feature_settings_list=feature_ind_settings,
                                   lag_settings_list=lag_ind_settings)

    features, targets, _ = fc_mgr.create_features_and_targets(instances=instances)

    features, targets, _ = select_windows(features=features, targets=targets)

    best_model = LinearVarModel(**best_params)

    best_model.fit(features, targets)

    return dict(best_model=best_model)


def inference_model(instances: pd.DataFrame,
                    best_model: LinearVarModel,
                    lag_ind_params: dict,
                    ):
    target_settings = TargetSettings()
    feature_ind_settings = []
    lag_ind_settings = [IndicatorLagSettings(**lag_ind_params)]

    fc_mgr = FeatureCreatorManager(target_settings=target_settings,
                                   feature_settings_list=feature_ind_settings,
                                   lag_settings_list=lag_ind_settings)

    features, _ = fc_mgr.create_features(instances=instances)
    features = features.dropna()
    if len(features) == 0:
        log.warning(f"features empty, likely instances too small. instances len: {len(instances)}")
        return []

    preds = best_model.predict(features)

    prediction_result = pd.DataFrame(data={"preds": preds}, index=features.index)

    return prediction_result
