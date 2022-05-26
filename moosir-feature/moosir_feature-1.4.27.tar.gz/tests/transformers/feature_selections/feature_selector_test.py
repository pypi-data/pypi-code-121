import pytest
import numpy as np
import pandas as pd

from moosir_feature.transformers.feature_selections.feature_selector import *


SAMPLE_N = 100
FEATURE_N = 10

@pytest.fixture
def features():
    return pd.DataFrame(data=np.random.rand(SAMPLE_N, FEATURE_N), columns=[ f"Feature_{i}" for i in range(FEATURE_N)])

@pytest.fixture
def targets():
    return pd.DataFrame(data=np.random.rand(SAMPLE_N, 1), columns=["Target"])


def test_remove_features_recursively(features, targets):
    # arrange
    n_features_to_select = 2

    # act
    result = remove_features_recursively(features=features, targets=targets, n_features_to_select=n_features_to_select)

    # assert
    print(result)
    assert len(result.columns) == n_features_to_select
