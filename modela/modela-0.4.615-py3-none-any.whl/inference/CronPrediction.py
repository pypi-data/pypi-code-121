import grpc
from github.com.metaprov.modelaapi.pkg.apis.inference.v1alpha1.generated_pb2 import CronPrediction as MDCronPrediction
from github.com.metaprov.modelaapi.services.cronprediction.v1.cronprediction_pb2_grpc import CronPredictionServiceStub
from github.com.metaprov.modelaapi.services.cronprediction.v1.cronprediction_pb2 import CreateCronPredictionRequest, \
    UpdateCronPredictionRequest, \
    DeleteCronPredictionRequest, GetCronPredictionRequest, ListCronPredictionsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class CronPrediction(Resource):
    def __init__(self, item: MDCronPrediction = MDCronPrediction(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class CronPredictionClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: CronPredictionServiceStub = stub

    def create(self, cronprediction: CronPrediction) -> bool:
        request = CreateCronPredictionRequest()
        request.cronprediction.CopyFrom(cronprediction.raw_message)
        try:
            response = self.__stub.CreateCronPrediction(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, cronprediction: CronPrediction) -> bool:
        request = UpdateCronPredictionRequest()
        request.cronprediction.CopyFrom(cronprediction.raw_message)
        try:
            self.__stub.UpdateCronPrediction(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[CronPrediction, bool]:
        request = GetCronPredictionRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetCronPrediction(request)
            return CronPrediction(response.cronprediction, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteCronPredictionRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteCronPrediction(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[CronPrediction], bool]:
        request = ListCronPredictionsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListCronPredictions(request)
            return [CronPrediction(item, self) for item in response.cronpredictions.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


