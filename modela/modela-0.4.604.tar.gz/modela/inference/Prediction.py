import grpc
from github.com.metaprov.modelaapi.pkg.apis.inference.v1alpha1.generated_pb2 import Prediction as MDPrediction
from github.com.metaprov.modelaapi.services.prediction.v1.prediction_pb2_grpc import PredictionServiceStub
from github.com.metaprov.modelaapi.services.prediction.v1.prediction_pb2 import CreatePredictionRequest, \
    UpdatePredictionRequest, \
    DeletePredictionRequest, GetPredictionRequest, ListPredictionsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Prediction(Resource):
    def __init__(self, item: MDPrediction = MDPrediction(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class PredictionClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: PredictionServiceStub = stub

    def create(self, prediction: Prediction) -> bool:
        request = CreatePredictionRequest()
        request.prediction.CopyFrom(prediction.raw_message)
        try:
            response = self.__stub.CreatePrediction(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, prediction: Prediction) -> bool:
        request = UpdatePredictionRequest()
        request.prediction.CopyFrom(prediction.raw_message)
        try:
            self.__stub.UpdatePrediction(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Prediction, bool]:
        request = GetPredictionRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetPrediction(request)
            return Prediction(response.prediction, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeletePredictionRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeletePrediction(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Prediction], bool]:
        request = ListPredictionsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListPredictions(request)
            return [Prediction(item, self) for item in response.predictions.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


