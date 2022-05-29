import pytest

from ml_project.ml_project.pipelines.models import train, ModelParams
from ml_project.ml_project.tests.utils import generate_sample_dataset


class TestModelsModule:
    def test_train(self):
        sample_dataset = generate_sample_dataset()
        model_params = ModelParams(model_type="LogisticRegression", params={})

        try:
            train(sample_dataset.features, sample_dataset.target, model_params)
        except Exception:
            pytest.fail("Problem with a configuration file.")
