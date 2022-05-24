import unittest
from modela import *

class Test_Modela_modelautobuilder(unittest.TestCase):
    """Tests for `modela.training.ModelAutobuilder`"""

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)

    @classmethod
    def tearDownClass(cls):
        cls.modela.close()

    def test_create(self):
        resource = self.modela.ModelAutobuilder(namespace="iris-product", name="test-mab",
                                                data_file="datasets/iris.csv",
                                                target_column="variety",
                                                task_type=TaskType.MultiClassification)
        resource.submit(replace=True)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(resource.wait_until_phase(ModelAutobuilderPhase.DatasetCompleted))
        assert resource.datasource.reference == ObjectReference("iris-product", "test-mab")
        assert resource.dataset.reference == ObjectReference("iris-product", "test-mab")
        loop.run_until_complete(resource.wait_until_phase(ModelAutobuilderPhase.StudyCompleted))
        assert resource.study.reference == ObjectReference("iris-product", "test-mab")
        loop.run_until_complete(resource.wait_until_phase(ModelAutobuilderPhase.Completed))
        assert resource.predictor.reference == ObjectReference("iris-product", "test-mab")
        resource.predictor.wait_until_ready()
        print(resource.predictor.predict(resource.dataset.test_prediction))
        resource.delete()


    def test_viz(self):
        resource = self.modela.ModelAutobuilder(namespace="iris-product", name="test-mab",
                                                data_file="datasets/iris.csv",
                                                target_column="variety",
                                                task_type=TaskType.MultiClassification)
        resource.submit_and_visualize(replace=True)
