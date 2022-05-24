import unittest
from modela import *


class Test_Modela_study(unittest.TestCase):
    """Tests for `modela.training.Study`"""
    resource: Study = None

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)

    @classmethod
    def tearDownClass(cls):
        cls.modela.close()

    def request_resource(self, name, **kwargs) -> Study:
        self.clear_resource()
        try:
            self.modela.Datasets.get("iris-product", "test-ds-gen")
        except ResourceNotFoundException:
            self.modela.Dataset(namespace="iris-product",
                                name="test-ds-gen",
                                data_file='datasets/iris.csv',
                                bucket="default-minio-bucket",
                                gen_datasource=True,
                                task_type=TaskType.MultiClassification,
                                target_column="variety").submit_and_visualize(replace=True)

        Test_Modela_study.resource = self.modela.Study(namespace="iris-product",
                                                       name=name,
                                                       dataset="test-ds-gen",
                                                       objective=Metric.Accuracy,
                                                       **kwargs)
        return Test_Modela_study.resource

    def clear_resource(self):
        if Test_Modela_study.resource:
            Test_Modela_study.resource.delete()
            Test_Modela_study.resource = None

    def test_0_create_actions(self):
        loop = asyncio.new_event_loop()
        study = self.request_resource("test-study")
        study.submit(replace=True)
        loop.run_until_complete(study.wait_until_phase(StudyPhase.EngineeringFeature))
        study.pause()
        time.sleep(1)
        assert study.status.Phase == StudyPhase.Paused
        study.resume()
        loop.run_until_complete(study.wait_until_phase(StudyPhase.EngineeringFeature))
        study.abort()
        time.sleep(1)
        assert study.status.Phase == StudyPhase.Aborted
        self.clear_resource()


    def test_1_viz(self):
        study = self.request_resource("test-study",
                                      search=ModelSearch(MaxTime=200, MaxModels=3, Trainers=2,
                                                         SearchSpace=AlgorithmSearchSpace(
                                                             Allowlist=[
                                                                 ClassicEstimator.LogisticRegression])),
                                      garbage_collect=False)
        study.submit_and_visualize(replace=True)

    def test_2_list(self):
        assert len(self.modela.Studies.list("iris-product")) >= 1
        assert len(Test_Modela_study.resource.models) > 0

    def test_3_update(self):
        Test_Modela_study.resource.set_label("test", "e")
        Test_Modela_study.resource.update()
        newStudy = self.modela.Study(namespace="iris-product", name="test-study")
        assert newStudy.has_label("test")

    def test_3_get(self):
        assert Test_Modela_study.resource.phase == StudyPhase.Completed
        assert Test_Modela_study.resource.best_model.spec.Estimator.AlgorithmName == "logistic-regression"



""" These tests should be run by an end-user on a functional terminal """
def test_viz():
    modela = Modela(port_forward=True)
    study = modela.Study(
        name="test-study-2",
        namespace="iris-product",
        dataset="iris",
        task_type=TaskType.MultiClassification,
        objective=Metric.Accuracy,
        bucket="default-minio-bucket",
        search=ModelSearch(MaxTime=200, MaxModels=8, Trainers=4))

    study.submit_and_visualize(replace=True)
    modela.close()
