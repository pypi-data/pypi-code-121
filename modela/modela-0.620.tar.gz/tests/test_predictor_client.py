import unittest

from modela.ModelaException import *
from modela.inference.Predictor import Predictor
from modela.inference.models import PredictorSpec
from modela.server import Modela
from modela import *


class Test_Modela_predictor(unittest.TestCase):
    """Tests for `modela.inference.Predictor`"""

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)
        return
        models = [model for model in cls.modela.Models.list("iris-product") if
                  model.phase in (ModelPhase.Completed, ModelPhase.Live)]
        if len(models) != 0:
            cls.model = models[0]
        else:
            cls.modela.Dataset(namespace="iris-product",
                               name="test-pred-gen-5",
                               data_file='datasets/iris.csv',
                               bucket="default-minio-bucket",
                               gen_datasource=True,
                               target_column="variety",
                               task_type=TaskType.MultiClassification,
                               fast=True).submit_and_visualize(replace=True)
            study = cls.modela.Study(namespace="iris-product",
                                     name="test-pred-gen-5",
                                     dataset="test-pred-gen-5", objective=Metric.Accuracy,
                                     search=ModelSearch(MaxTime=200, MaxModels=1, Trainers=1),
                                     fe_search=FeatureEngineeringSearch(Enabled=False),
                                     fast=True)
            study.submit_and_visualize(replace=True)
            cls.model = study.best_model

    @classmethod
    def tearDownClass(cls):
        cls.modela.close()

    def test_0_create(self):
        predictor = self.modela.Predictor(namespace="iris-product", name="p-model-20220511-153544")#"test-pred", model=Test_Modela_predictor.model)
        predictor.submit(replace=True)

    def test_1_list(self):
        assert len(self.modela.Predictors.list("iris-product")) >= 1

    def test_2_update(self):
        predictor = self.modela.Predictor(namespace="iris-product", name="test-pred")
        predictor.set_label("test", "e")
        predictor.update()
        newds = self.modela.Predictor(namespace="iris-product", name="test-pred")
        assert newds.has_label("test")

    def test_3_predict(self):
        predictor = self.modela.Predictor(namespace="iris-product", name="test-pred")
        predictor.submit(replace=True)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(predictor.wait_until_ready())
        print(predictor.predict(predictor.model.test_prediction))


    def test_4_delete(self):
        predictor = self.modela.Predictor(namespace="iris-product", name="test-pred")
        predictor.delete()
        self.assertRaises(ResourceNotFoundException, self.modela.Studies.get, "iris-product", "test")
