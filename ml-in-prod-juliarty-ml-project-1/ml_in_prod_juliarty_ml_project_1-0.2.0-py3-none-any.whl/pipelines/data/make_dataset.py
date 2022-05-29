import os.path

import pandas as pd
import numpy as np
import logging
import gdown

from typing import Tuple, Union
from sklearn.model_selection import train_test_split
from .features_params import (
    FeatureParams,
    NumericalFeatureParams,
    CategoricalFeatureParams,
)
from .split_params import SplittingParams

logger = logging.getLogger(__name__)


def download_data(output_data_path: str) -> None:
    """
    If file doesn't exist, it will be downloaded from Google Drive.
    Args:
        output_data_path: The path to write the file.
    """
    if not os.path.exists(output_data_path):
        data_url = "https://drive.google.com/uc?id=1Pw3650ra8hVTb9Ybf4WxjbOcVi8oFI8l"
        gdown.download(data_url, output_data_path, quiet=False)


def load_data(
    data_path: str, feature_params: FeatureParams, with_target=False
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.Series]]:
    """
    Gets features and target from **.csv** file according `feature_params`.
    Args:
        with_target: Whether to add target column to output
        feature_params: Describes all features and target to be included.
        data_path: Path to a csv file.

    Returns: (features, target) or target.
    """
    df = pd.read_csv(data_path)

    feature_columns = [
        column
        for column in feature_params.all_features
        if column not in feature_params.features_to_drop
    ]
    logging.info(f"Number of features: {len(feature_columns)}")
    if with_target:
        return df[feature_columns], df[feature_params.target.name]
    else:
        return df[feature_columns]


def split_data(
    features: Union[pd.DataFrame, np.ndarray],
    target: Union[pd.Series, np.ndarray],
    split_params: SplittingParams,
) -> Tuple[
    Union[pd.DataFrame, np.ndarray],
    Union[pd.DataFrame, np.ndarray],
    Union[pd.Series, np.ndarray],
    Union[pd.Series, np.ndarray],
]:
    """
    Splits features, target on train, test.

    Returns: Tuple (features_train, features_test, target_train, target_test)
    """
    features_train, features_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=split_params.test_size,
        random_state=split_params.random_state,
    )
    logger.info(f"Split data. Test size: {split_params.test_size}")
    return features_train, features_test, y_train, y_test


def generate_numerical_samples(
    samples_num: int, feature_params: NumericalFeatureParams
) -> np.ndarray:
    if feature_params.type == "discrete":
        return np.random.choice(
            range(int(feature_params.min), int(feature_params.max) + 1), samples_num
        )
    elif feature_params.type == "continuous":
        return np.random.random(samples_num) * (feature_params.max - feature_params.min)
    else:
        error_message = f"Unknown number type {feature_params.type}."
        logger.error(error_message)
        raise ValueError(error_message)


def generate_categorical_samples(
    samples_num: int, feature_params: CategoricalFeatureParams
) -> np.ndarray:
    return np.random.choice(feature_params.categories, samples_num)


def generate_train_data(
    samples_num: int,
    feature_params: FeatureParams,
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Generates features and target that are described in `feature_params`.
    Args:
        samples_num: Number of samples to generate.
        feature_params: Feature description

    Returns: (features, target)
    """
    feature_name_to_samples = {}
    for num_feature_params in feature_params.numerical_features:
        feature_name_to_samples[num_feature_params.name] = generate_numerical_samples(
            samples_num, num_feature_params
        )

    for cat_feature_params in feature_params.categorical_features:
        feature_name_to_samples[cat_feature_params.name] = generate_categorical_samples(
            samples_num, cat_feature_params
        )

    features = pd.DataFrame(
        {name: feature_name_to_samples[name] for name in feature_params.all_features}
    )
    targets = np.random.choice(feature_params.target.categories, samples_num)
    return features, pd.Series(targets)
