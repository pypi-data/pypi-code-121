import time
import unittest

from modela.ModelaException import *
from modela.data.Dataset import Dataset
from modela.server import Modela
from modela import *
from modela.util import convert_size

from google.protobuf.json_format import MessageToJson


class Test_Modela_dataset(unittest.TestCase):
    """Tests for `modela.data.Dataset`"""
    resource: Dataset = None

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)

    @classmethod
    def tearDownClass(cls):
        cls.modela.close()

    def request_resource(self, name, **kwargs) -> Dataset:
        self.clear_resource()
        Test_Modela_dataset.resource = self.modela.Dataset(namespace="iris-product",
                                                           name=name,
                                                           data_file='datasets/heart.csv',
                                                           bucket="default-minio-bucket",
                                                           task_type=TaskType.BinaryClassification,
                                                           **kwargs)
        return Test_Modela_dataset.resource

    def clear_resource(self):
        if Test_Modela_dataset.resource:
            Test_Modela_dataset.resource.delete()
            Test_Modela_dataset.resource = None

    def test_0_create_from_ds(self):
        datasource = self.modela.DataSource(namespace="iris-product", name="test-create-ds",
                                            infer_file='datasets/heart.csv',
                                            target_column="target",
                                            task_type=TaskType.BinaryClassification)
        datasource.submit(replace=True)
        dataset = self.request_resource("test-ds-0", datasource=datasource)
        dataset.submit(replace=True)
        assert len(self.modela.Datasets.list("iris-product")) >= 1
        assert dataset.datasource.reference == datasource.reference
        self.clear_resource()
        datasource.delete()
        time.sleep(0.5)
        self.assertRaises(ResourceNotFoundException, self.modela.Datasets.get, "iris-product", "test-ds-0")

    def test_0_create_gen_ds(self):
        dataset = self.request_resource("test-ds-gen", gen_datasource=True, target_column="target")
        dataset.submit(replace=True)
        assert len(self.modela.Datasets.list("iris-product")) >= 1
        assert len(self.modela.DataSources.list("iris-product")) >= 1
        ds = self.modela.DataSources.get("iris-product", "test-ds-gen-source")
        assert len(ds.schema.Columns) == 14
        assert dataset.datasource.reference == ds.reference
        assert dataset.datasource.spec.Task == TaskType.BinaryClassification
        self.clear_resource()

    def test_1_viz(self):
        dataset = self.request_resource("test-ds-gen", gen_datasource=True, target_column="target")
        dataset.submit_and_visualize(replace=True)
        assert dataset.phase == DatasetPhase.Ready

    def test_2_list(self):
        assert len(self.modela.Datasets.list("iris-product")) >= 1

    def test_2_print(self):
        print(Test_Modela_dataset.resource)

    def test_2_payload(self):
        print(Test_Modela_dataset.resource.test_prediction)

    def test_2_profile(self):
        print(Test_Modela_dataset.resource.profile)

    def test_2_report(self):
        print(Test_Modela_dataset.resource.report)

    def test_3_update(self):
        Test_Modela_dataset.resource.set_label("test2", "e")
        Test_Modela_dataset.resource.update()
        newDs = self.modela.Dataset(namespace="iris-product", name="test-ds-gen")
        assert newDs.has_label("test2")


""" These tests should be run by an end-user. """


def test_viz():
    modela = Modela(port_forward=True)
    datasource = modela.DataSource(namespace="iris-product", name="iris")
    dataset = modela.Dataset(namespace="iris-product", name="test-ds-5", data_file='tests/datasets/iris.csv',
                             datasource=datasource, task_type=TaskType.MultiClassification)

    dataset.submit_and_visualize(replace=True)
    modela.close()
