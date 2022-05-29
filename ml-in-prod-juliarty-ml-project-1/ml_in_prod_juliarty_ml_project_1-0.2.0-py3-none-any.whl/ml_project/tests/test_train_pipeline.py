from .utils import prepare_dataset
from ..pipelines.train_pipeline_params import (
    get_training_pipeline_params,
    TrainingPipelineParams,
)
from ..pipelines.train_pipeline import start_training_pipeline
import yaml
import pytest
import os

from ..pipelines.utils import create_directory

TEST_DIR = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(TEST_DIR, "test_data")
TEST_CONFIG_PATH = os.path.join(TEST_DATA_PATH, "train_config.yaml")


def load_config(config_path: str) -> TrainingPipelineParams:
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)
        return get_training_pipeline_params(config_dict)


class TestTrainPipeline:
    def test_get_training_pipeline_params(self):
        try:
            load_config(TEST_CONFIG_PATH)
        except Exception:
            pytest.fail("Problem with a configuration file.")

    def test_train_pipeline(self):
        pipeline_params = load_config(TEST_CONFIG_PATH)
        prepare_dataset(pipeline_params)
        create_directory(pipeline_params.output_model_path)
        start_training_pipeline(pipeline_params)

        os.remove(pipeline_params.input_data_path)
