import unittest

from modela.ModelaException import *
from modela.training.Report import Report
from modela.server import Modela
from modela import *

class Test_Modela_report(unittest.TestCase):
    """Tests for `modela.training.Report`"""

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)

    @classmethod
    def tearDownClass(cls):
        cls.modela.close()

    def test_1_list(self):
        assert len(self.modela.Reports.list("iris-product")) >= 1

    def test_2_get(self):
        report = self.modela.Report(namespace="iris-product", name="test")
        spec = report.spec
        assert type(spec) == ReportSpec

    def test_3_download(self):
        report = self.modela.Reports.list("iris-product")[0]
        assert len(report.download()) > 1000

