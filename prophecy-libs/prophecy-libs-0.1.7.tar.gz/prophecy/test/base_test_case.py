import unittest
from pyspark.sql import SparkSession


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.master("local").appName("init").getOrCreate()
        cls.maxUnequalRowsToShow = 5

    def setup(self):
        self.spark = BaseTestCase.spark
        self.maxUnequalRowsToShow = BaseTestCase.maxUnequalRowsToShow