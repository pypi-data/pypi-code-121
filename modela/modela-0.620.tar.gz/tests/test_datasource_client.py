import time
import unittest

import pandas

from modela.ModelaException import *
from modela.data.DataSource import DataSource
from modela.data.common import DataType
from modela.data.models import DataSourceSpec, Column
from modela.server import Modela
from modela.training.common import Imputation, TaskType


class Test_Modela_datasource(unittest.TestCase):
    """Tests for `modela.data.DataSource`"""
    resource: DataSource = None

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)

    @classmethod
    def tearDownClass(cls):
        cls.clear_resource(cls)
        cls.modela.close()

    def request_resource(self, name, **kwargs) -> DataSource:
        self.clear_resource()
        Test_Modela_datasource.resource = self.modela.DataSource(namespace="iris-product",
                                                                 name=name,
                                                                 bucket="default-minio-bucket",
                                                                 **kwargs)

        return Test_Modela_datasource.resource

    def clear_resource(self):
        if Test_Modela_datasource.resource:
            Test_Modela_datasource.resource.delete()
            Test_Modela_datasource.resource = None

    def test_infer_api(self):
        with open('datasets/iris.csv') as f:
            data = f.read()

        loc = self.modela.FileService.upload_file("iris.csv", data, "default-tenant", "iris-product", "v0.0.1",
                                                  "default-minio-bucket", "datasources", "test")
        infer = self.modela.DataSources.infer("iris-product", loc)
        assert infer[0].Name == 'sepal.length'

    def test_0_create(self):
        resource = self.request_resource("test", task_type=TaskType.Regression)
        resource.submit(replace=True)
        time.sleep(0.5)
        resource = self.modela.DataSource(namespace="iris-product", name="test")
        assert resource.spec.Task == TaskType.Regression
        self.clear_resource()

    def test_0_infer_file(self):
        resource = self.request_resource("test", infer_file='datasets/iris.csv', target_column="variety")
        resource.submit(replace=True)
        resource = self.modela.DataSource(namespace="iris-product", name="test")
        assert resource.spec.Schema.Columns[0].Name == 'sepal.length'
        assert resource.spec.Schema.Columns[4].Target
        self.clear_resource()

    def test_0_infer_bytes(self):
        with open('datasets/iris.csv', 'rb') as f:
            data = f.read()

        resource = self.request_resource("test", infer_file='datasets/iris.csv', infer_bytes=data, target_column="variety")
        resource.submit(replace=True)
        resource = self.modela.DataSource(namespace="iris-product", name="test")
        assert resource.spec.Schema.Columns[0].Name == 'sepal.length'
        assert resource.spec.Schema.Columns[4].Target
        self.clear_resource()

    def test_1_create_infer_df(self):
        df = pandas.read_csv('datasets/iris.csv')
        resource = self.request_resource("test", infer_dataframe=df, target_column="variety")
        resource.submit(replace=True)
        resource = self.modela.DataSource(namespace="iris-product", name="test")
        assert resource.spec.Schema.Columns[0].Name == 'sepal.length'
        assert resource.spec.Schema.Columns[4].Target

    def test_2_list(self):
        assert len(self.modela.DataSources.list("iris-product")) >= 1

    def test_2_update(self):
        Test_Modela_datasource.resource.spec.Schema.Columns.append(
            Column("col", DataType.Text, Imputation=Imputation.ReplaceWithMean, SkewThreshold=4, Enum=["1", "2"]))
        Test_Modela_datasource.resource.update()
        ds = self.modela.DataSource(namespace="iris-product", name="test")
        assert ds.spec.Schema.Columns[5].Imputation == Imputation.ReplaceWithMean

    def test_3_get(self):
        datasource = self.modela.DataSource(namespace="iris-product", name="test")
        spec = datasource.spec
        assert datasource['sepal.length'] == Test_Modela_datasource.resource.spec.Schema.Columns[0]
        assert datasource.target_column == Test_Modela_datasource.resource.spec.Schema.Columns[4]
        self.clear_resource()