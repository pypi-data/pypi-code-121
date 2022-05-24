import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import Featureset as MDFeatureset
from github.com.metaprov.modelaapi.services.featureset.v1.featureset_pb2_grpc import FeaturesetServiceStub
from github.com.metaprov.modelaapi.services.featureset.v1.featureset_pb2 import CreateFeaturesetRequest, \
    UpdateFeaturesetRequest, \
    DeleteFeaturesetRequest, GetFeaturesetRequest, ListFeaturesetRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Featureset(Resource):
    def __init__(self, item: MDFeatureset = MDFeatureset(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name)


class FeaturesetClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: FeaturesetServiceStub = stub

    def create(self, featureset: Featureset) -> bool:
        request = CreateFeaturesetRequest()
        request.featureset.CopyFrom(featureset.raw_message)
        try:
            response = self.__stub.CreateFeatureset(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, featureset: Featureset) -> bool:
        request = UpdateFeaturesetRequest()
        request.featureset.CopyFrom(featureset.raw_message)
        try:
            self.__stub.UpdateFeatureset(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Featureset, bool]:
        request = GetFeaturesetRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetFeatureset(request)
            return Featureset(response.featureset, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteFeaturesetRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteFeatureset(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Featureset], bool]:
        request = ListFeaturesetRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListFeaturesets(request)
            return [Featureset(item, self) for item in response.featuresets.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


