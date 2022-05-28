import csv
import os
import pickle
from typing import List, Union

import pandas as pd

from dataclasses import dataclass
from ml_project.src.pipelines.data import FeatureParams, generate_train_data, load_data
from ml_project.src.pipelines.data.features_params import (
    NumericalFeatureParams,
    CategoricalFeatureParams,
)
from ml_project.src.pipelines.models.train_model import create_model
from ml_project.src.pipelines.predict_pipeline_params import PredictPipelineParams
from ml_project.src.pipelines.preprocessing import (
    create_transformer,
    CustomTransformerClass,
)
from ml_project.src.pipelines.train_pipeline_params import TrainingPipelineParams
from ml_project.src.pipelines.utils import create_directory


def prepare_dataset(
    pipeline_params: Union[TrainingPipelineParams, PredictPipelineParams]
) -> None:
    """
    Saves a randomly generated dateset with features
    that correspond to `features_params`.

    The dataset is saved in the file `file_path` in .csv format.
    """
    create_directory(pipeline_params.input_data_path)
    samples_num = 128
    features, target = generate_train_data(samples_num, pipeline_params.features)
    with open(pipeline_params.input_data_path, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=",")
        csv_writer.writerow(
            list(features.columns.values) + [pipeline_params.features.target.name]
        )
        for i in range(len(features)):
            # Generator is used because iloc() and loc()
            # change the type of all features to float64
            csv_writer.writerow(
                [features[name][i] for name in list(features.columns.values)]
                + [target[i]]
            )


def prepare_transformer(pipeline_params: PredictPipelineParams):
    categorical_features = [
        f.name for f in pipeline_params.features.categorical_features
    ]
    numerical_features = [f.name for f in pipeline_params.features.numerical_features]
    transformer = create_transformer(
        pipeline_params.preprocessing,
        categorical_features=categorical_features,
        numerical_features=numerical_features,
    )

    features = load_data(
        pipeline_params.input_data_path, pipeline_params.features, with_target=False
    )

    transformer.fit(features)
    with open(pipeline_params.transformer_path, "wb") as f:
        pickle.dump(transformer, f)


def prepare_model(pipeline_params: PredictPipelineParams) -> None:
    create_directory(pipeline_params.model_path)
    model = create_model(pipeline_params.model)
    features, targets = load_data(
        pipeline_params.input_data_path, pipeline_params.features, with_target=True
    )

    with open(pipeline_params.transformer_path, "rb") as f:
        transformer: CustomTransformerClass = pickle.load(f)

    features = transformer.transform(features)

    model.fit(features, targets)
    with open(pipeline_params.model_path, "wb") as f:
        pickle.dump(model, f)


def prepare_predict_artefacts(pipeline_params: PredictPipelineParams):
    prepare_dataset(pipeline_params)
    prepare_transformer(pipeline_params)
    prepare_model(pipeline_params)


def remove_predict_artefacts(pipeline_params: PredictPipelineParams):
    os.remove(pipeline_params.input_data_path)
    os.remove(pipeline_params.model_path)
    os.remove(pipeline_params.transformer_path)


@dataclass()
class SampleDataset:
    features: pd.DataFrame
    target: pd.Series
    discrete_features: List[NumericalFeatureParams]
    continuous_features: List[NumericalFeatureParams]
    categorical_features: List[CategoricalFeatureParams]
    target_params: CategoricalFeatureParams


def generate_sample_dataset() -> SampleDataset:
    discrete_feature_range = [-100, 100]
    categorical_features_categories = [0, 1, 2]
    continuous_feature_range = [0, 1]
    target_categories = [0, 1]
    discrete_1 = NumericalFeatureParams(
        name="discrete_1",
        type="discrete",
        min=discrete_feature_range[0],
        max=discrete_feature_range[1],
    )

    continuous_1 = NumericalFeatureParams(
        name="continuous_1",
        type="continuous",
        min=continuous_feature_range[0],
        max=continuous_feature_range[1],
    )

    categorical_1 = CategoricalFeatureParams(
        name="cat_1", categories=categorical_features_categories
    )
    target_feature_params = CategoricalFeatureParams(
        name="target", categories=target_categories
    )

    feature_params = FeatureParams(
        all_features=[
            discrete_1.name,
            continuous_1.name,
            categorical_1.name,
        ],
        numerical_features=[discrete_1, continuous_1],
        categorical_features=[categorical_1],
        target=target_feature_params,
        features_to_drop=[],
    )
    features, target = generate_train_data(100, feature_params)

    categorical_features = [categorical_1]
    discrete_features = [discrete_1]
    continuous_feature = [continuous_1]
    return SampleDataset(
        features=features,
        target=target,
        discrete_features=discrete_features,
        continuous_features=continuous_feature,
        categorical_features=categorical_features,
        target_params=target_feature_params,
    )
