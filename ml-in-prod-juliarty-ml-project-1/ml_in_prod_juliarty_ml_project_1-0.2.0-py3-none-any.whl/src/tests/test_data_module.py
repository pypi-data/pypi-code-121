import numpy as np
import pandas as pd

from ml_project.ml_project.pipelines.data.features_params import (
    NumericalFeatureParams,
    CategoricalFeatureParams,
)
from ml_project.ml_project.tests.utils import generate_sample_dataset


def check_numerical_feature(values: pd.Series, feature_params: NumericalFeatureParams):
    if feature_params.type == "discrete":
        assert values.dtype == np.int64 or values.dtype == np.int32
    elif feature_params.type == "continuous":
        assert values.dtype == np.float64 or values.dtype == np.float32
    else:
        assert False

    assert np.all(
        np.logical_and(
            values >= feature_params.min,
            values <= feature_params.max,
        )
    )


def check_categorical_feature(
    values: pd.Series, feature_params: CategoricalFeatureParams
):
    assert np.all(values.apply(lambda x: x in feature_params.categories))


class TestDataModule:
    def test_data_generation(self):
        sample_dataset = generate_sample_dataset()

        for discrete_feature in sample_dataset.discrete_features:
            check_numerical_feature(
                sample_dataset.features[discrete_feature.name], discrete_feature
            )

        for continuous_feature in sample_dataset.continuous_features:
            check_numerical_feature(
                sample_dataset.features[continuous_feature.name], continuous_feature
            )

        for categorical_features in sample_dataset.categorical_features:
            check_categorical_feature(
                sample_dataset.features[categorical_features.name], categorical_features
            )

        check_categorical_feature(sample_dataset.target, sample_dataset.target_params)
