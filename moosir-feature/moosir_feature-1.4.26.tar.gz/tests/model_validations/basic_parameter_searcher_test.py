import pandas as pd
import numpy as np
import pytest
from sklearn.dummy import DummyRegressor

from moosir_feature.model_validations.basic_parameter_searcher import ParameterSearcher


def test_run_parameter_search():
    # arrange
    sample_n = 100
    feature_n = 1

    feature_cols = [f"f_{i}" for i in range(feature_n)]
    target_col = "target"
    features = pd.DataFrame(data=np.arange(0, sample_n * feature_n).reshape(sample_n, -1), columns=feature_cols)
    targets = pd.DataFrame(data=np.arange(0, sample_n * 1).reshape(sample_n, -1), columns=[target_col])

    # arrange params
    cv_params = {"train_lengths": [6],
                 "test_lengths": [3],
                 "look_aheads": [1],
                 "train_shuffle_block_size": [2]}

    estimator = DummyRegressor(strategy="mean")

    param_grid = {"strategy": ["mean", "median"]}

    metrics = ["neg_mean_squared_error"]

    searcher = ParameterSearcher()

    # act
    grid_results = searcher.run_parameter_search_multiple_cvs(X=features,
                                                              y=targets,
                                                              estimator=estimator,
                                                              cv_params=cv_params,
                                                              param_grid=param_grid,
                                                              metrics=metrics,
                                                              )

    # assert
    print(grid_results)
    # print(best_models)


def test_search_params():
    # arrange
    sample_n = 100
    feature_n = 1
    train_n = 70
    test_n = 25

    feature_cols = [f"f_{i}" for i in range(feature_n)]
    target_col = "target"
    features = pd.DataFrame(data=np.arange(0, sample_n * feature_n).reshape(sample_n, -1), columns=feature_cols)
    targets = pd.DataFrame(data=np.arange(0, sample_n * 1).reshape(sample_n, -1), columns=[target_col])

    # arrange params
    estimator = DummyRegressor(strategy="mean")
    param_grid = {"strategy": ["mean", "median"]}
    metrics = ["neg_mean_squared_error"]

    searcher = ParameterSearcher()

    # act
    cv_result, grid = searcher.search_params(X=features,
                                             y=targets,
                                             estimator=estimator,
                                             param_grid=param_grid,
                                             metrics=metrics,
                                             train_size=train_n,
                                             test_size=test_n,
                                             is_get_best_model=False,
                                             return_train_score=True,
                                             train_shuffle_block_size=None)

    # assert
    print(cv_result)
    print(grid)
