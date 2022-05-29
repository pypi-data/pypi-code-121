from .utils import prepare_predict_artefacts, remove_predict_artefacts
from ..pipelines.predict_pipeline_params import (
    PredictPipelineParams,
    get_predict_pipeline_params,
)

from ..pipelines.predict_pipeline import start_predict_pipeline
import yaml
import pytest
import os


TEST_DIR = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(TEST_DIR, "test_data")
TEST_CONFIG_PATH = os.path.join(TEST_DATA_PATH, "predict_config.yaml")


def load_config(config_path: str) -> PredictPipelineParams:
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)
        return get_predict_pipeline_params(config_dict)


class TestPredictPipeline:
    def test_get_predict_pipeline_params(self):
        try:
            load_config(TEST_CONFIG_PATH)
        except Exception:
            pytest.fail("Problem with a configuration file.")

    def test_predict_pipeline(self):
        pipeline_params = load_config(TEST_CONFIG_PATH)

        prepare_predict_artefacts(pipeline_params)

        start_predict_pipeline(pipeline_params)

        remove_predict_artefacts(pipeline_params)
