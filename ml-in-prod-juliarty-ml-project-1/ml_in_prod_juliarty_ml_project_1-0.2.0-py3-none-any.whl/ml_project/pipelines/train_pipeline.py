import pickle
import hydra
import json
import numpy as np
import pandas as pd
import logging

from omegaconf import DictConfig
from typing import Union, Any
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from .preprocessing import create_transformer
from .utils import create_directory, init_hydra, get_pipeline
from .data import load_data, split_data, download_data
from .train_pipeline_params import get_training_pipeline_params, TrainingPipelineParams
from .models import SklearnClassifierModel, train

logger = logging.getLogger(__name__)

metrics_to_score_func = {
    "f1-score": f1_score,
    "accuracy": accuracy_score,
    "roc-auc": roc_auc_score,
}


def get_metrics(pipeline_params: TrainingPipelineParams) -> dict:
    metrics = {}

    for metric_name in pipeline_params.metric:
        if metric_name not in metrics_to_score_func.keys():
            logger.warning(f"Unknown metric: {metric_name}.")
            continue
        metrics[metric_name] = metrics_to_score_func[metric_name]

    return metrics


def validate_model(
    model: SklearnClassifierModel,
    feature_val: Union[pd.DataFrame, np.ndarray],
    target_val: Union[pd.Series, np.ndarray],
    pipeline_params: TrainingPipelineParams,
) -> dict:
    target_predicted = model.predict(feature_val)
    metrics = get_metrics(pipeline_params)

    metric_scores = {}

    for metric_name in metrics.keys():
        score_func = metrics[metric_name]
        metric_scores[metric_name] = score_func(target_predicted, target_val)

    return metric_scores


def pickle_object(obj: Any, file_path: str):
    create_directory(file_path)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)


def save_metrics(metrics: dict, pipeline_params: TrainingPipelineParams) -> None:
    create_directory(pipeline_params.metric_path)
    with open(pipeline_params.metric_path, "w") as f:
        json.dump(metrics, f)


@hydra.main(config_path="configs", config_name="default_train_pipeline.yaml")
def start_training_pipeline(cfg: Union[DictConfig, TrainingPipelineParams]) -> dict:
    init_hydra()

    logger.info("Started training.")

    logger.info("Parse the config.")

    if isinstance(cfg, TrainingPipelineParams):
        pipeline_params = cfg
    else:
        pipeline_params = get_training_pipeline_params(dict(cfg))

    logger.info("Download data.")
    download_data(pipeline_params.input_data_path)

    logger.info("Load data.")
    features, target = load_data(
        pipeline_params.input_data_path, pipeline_params.features, True
    )

    logger.info("Splitting data.")
    features_train, features_test, target_train, target_test = split_data(
        features, target, pipeline_params.split
    )

    logger.info("Preprocessing data.")
    categorical_features = [
        f.name for f in pipeline_params.features.categorical_features
    ]
    numerical_features = [f.name for f in pipeline_params.features.numerical_features]
    transformer = create_transformer(
        params=pipeline_params.preprocessing,
        categorical_features=categorical_features,
        numerical_features=numerical_features,
    )

    features_train = transformer.fit_transform(features_train)
    logger.info(f"Fit transformer: {transformer.__str__()}")

    logger.info("Fitting model.")
    model = train(features_train, target_train, pipeline_params.model)

    logger.info("Validating model.")
    features_test = transformer.transform(features_test)
    metrics = validate_model(model, features_test, target_test, pipeline_params)
    logger.info(f"Metrics: {metrics}")

    if pipeline_params.save_output:
        logger.info("Saving results.")
        save_metrics(metrics, pipeline_params)
        pipeline = get_pipeline(transformer, model)
        pickle_object(pipeline, pipeline_params.output_model_path)

    return metrics


if __name__ == "__main__":
    start_training_pipeline()
