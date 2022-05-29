import numpy as np

from .utils import generate_sample_dataset
from ..pipelines.preprocessing.transformers import OneHotTransformer


class TestTransformers:
    def test_one_hot_transformer(self):
        sample_dataset = generate_sample_dataset()
        numerical_features = [f.name for f in sample_dataset.discrete_features] + [
            f.name for f in sample_dataset.continuous_features
        ]
        scale = True
        transformer = OneHotTransformer(
            categorical_features=[f.name for f in sample_dataset.categorical_features],
            numerical_features=numerical_features,
            scale=scale,
        )

        transformer = transformer.fit(sample_dataset.features)
        transformed_features = transformer.transform(sample_dataset.features)

        one_hot_features = 0
        for categorical_feature in sample_dataset.categorical_features:
            one_hot_features += len(categorical_feature.categories)

        expected_feature_num = (
            len(sample_dataset.discrete_features)
            + len(sample_dataset.continuous_features)
            + one_hot_features
        )
        assert len(transformed_features.columns) == expected_feature_num
        if scale:
            standard_mean = 0
            standard_std = 1
            eps = 1e-1
            for feature in (
                sample_dataset.discrete_features + sample_dataset.continuous_features
            ):
                assert np.isclose(
                    transformed_features[feature.name].mean(), standard_mean, rtol=eps
                )
                assert np.isclose(
                    transformed_features[feature.name].std(), standard_std, rtol=eps
                )
