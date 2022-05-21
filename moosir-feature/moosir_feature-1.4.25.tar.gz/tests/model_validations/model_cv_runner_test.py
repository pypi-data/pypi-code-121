from moosir_feature.model_validations.benchmarking import RandomModel
from moosir_feature.model_validations.model_cv_runner import *

import pytest
import pandas as pd
import numpy as np
from moosir_feature.model_validations.model_validator import CustomTsCv
from sklearn.dummy import DummyRegressor


def test_predict_on_cv():

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

    model = DummyRegressor(strategy="mean")
    cv = CustomTsCv(train_n=10, test_n=3, sample_n=sample_n, train_shuffle_block_size=None)

    # act
    result = predict_on_cv(model=model, features=features, targets=targets, cv=cv)

    # assert
    assert len(result) == sample_n
    assert len(result.columns) == len(result.columns)






