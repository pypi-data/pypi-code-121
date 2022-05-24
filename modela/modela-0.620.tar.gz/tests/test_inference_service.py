import unittest

from modela.ModelaException import *
from modela.inference.InferenceService import InferenceService
from modela.training.Model import Model
from modela.server import Modela
from modela.training.models import ModelSpec
import pprint
from modela import *

class Test_Modela_model(unittest.TestCase):
    """Tests for `modela.training.Model`"""

    @classmethod
    def setUpClass(cls):
        cls.modela = Modela(port_forward=True)

    @classmethod
    def tearDownClass(cls):
        cls.modela.close()

    def test_connect_predictor(self):
        predictor = self.modela.Predictor("iris-product", "test-ingress")
        #serve = predictor.connect()
        serve = InferenceService("serving.vcap.me", secure=True, tls_cert='tests/inference_server.crt')
        predictions = serve.predict("iris-product", "model-20220219-002120",
                                             "[{\"sepal.length\":4.6, \"sepal.width\":3.2, \"petal.length\":1.0, \"petal.width\":0.3}]",
                                    explain=True)
        print(predictions)
        assert predictions[0].Label == "Setosa"
