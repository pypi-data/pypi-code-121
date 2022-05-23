"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline, pipeline
from kedro_mlflow.pipeline import pipeline_ml_factory

from .pipelines import etl_app as etl
from .pipelines import ml_app as mls
from .pipelines import user_app as user


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    etl_pipeline = etl.create_pipeline()

    ml_pipeline = mls.create_pipeline()

    ml_infer_pipeline = ml_pipeline.only_nodes_with_tags("inference")
    ml_train_pipeline = ml_pipeline.only_nodes_with_tags("training")

    ml_search_pipeline = ml_pipeline.only_nodes_with_tags("searching")

    ml_benchmarking_pipeline = ml_pipeline.only_nodes_with_tags("benchmarking")

    ml_alphas_pipeline = ml_pipeline.only_nodes_with_tags("alphas")

    user_pipeline = user.create_pipeline()

    training_pipeline_ml = pipeline_ml_factory(
        training=ml_train_pipeline,
        inference=ml_infer_pipeline,
        input_name="instances",
    )

    return {
        "etl": etl_pipeline,
        "alphas": ml_alphas_pipeline,
        "search": ml_search_pipeline,
        "benchmark": ml_benchmarking_pipeline,
        "train": training_pipeline_ml,
        "infer": ml_infer_pipeline,
        "user": user_pipeline,
        "__default__": etl_pipeline + training_pipeline_ml + ml_search_pipeline + ml_benchmarking_pipeline + ml_infer_pipeline
    }
