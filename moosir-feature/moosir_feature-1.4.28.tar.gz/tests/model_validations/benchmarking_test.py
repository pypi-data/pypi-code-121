import pandas as pd
import numpy as np
import pytest
from sklearn.dummy import DummyRegressor

from moosir_feature.model_validations.benchmarking import RandomModel, run_benchmarking, NaiveModel

from moosir_feature.model_validations.model_validator import CustomTsCv


# @pytest.mark.skip()
def test_random_with_cv():
    # arrange
    sample_n = 100
    feature_n = 1

    feature_cols = [f"f_{i}" for i in range(feature_n)]
    target_col = "target"
    features = pd.DataFrame(data=np.arange(0, sample_n * feature_n).reshape(sample_n, -1),
                            columns=feature_cols,
                            index=pd.date_range("2000/01/01", periods=sample_n))
    targets = pd.DataFrame(data=np.arange(0, sample_n * 1).reshape(sample_n, -1),
                           columns=[target_col],
                           index=pd.date_range("2000/01/01", periods=sample_n))

    # arrange model and cv
    min = targets.min()
    max = targets.max()

    models = [RandomModel(min=min, max=max), NaiveModel(targets=targets.copy(), look_back_len=1)]

    cv = CustomTsCv(train_n=10, test_n=3, sample_n=sample_n, train_shuffle_block_size=None)

    metrics = ['neg_mean_absolute_percentage_error',
               'neg_mean_absolute_error',
               'binary_returns_avg',
               'binary_returns']

    # act
    result = run_benchmarking(models=models, targets=targets, features=features, cv=cv, metrics=metrics)

    # assert
    print(result)
