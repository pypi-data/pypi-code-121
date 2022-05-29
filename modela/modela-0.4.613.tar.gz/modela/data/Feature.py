import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import Feature as MDFeature
from github.com.metaprov.modelaapi.services.feature.v1.feature_pb2_grpc import FeatureServiceStub
from github.com.metaprov.modelaapi.services.feature.v1.feature_pb2 import CreateFeatureRequest, \
    UpdateFeatureRequest, \
    DeleteFeatureRequest, GetFeatureRequest, ListFeaturesRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Feature(Resource):
    def __init__(self, item: MDFeature = MDFeature(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class FeatureClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: FeatureServiceStub = stub

    def create(self, feature: Feature) -> bool:
        request = CreateFeatureRequest()
        request.feature.CopyFrom(feature.raw_message)
        try:
            response = self.__stub.CreateFeature(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, feature: Feature) -> bool:
        request = UpdateFeatureRequest()
        request.feature.CopyFrom(feature.raw_message)
        try:
            self.__stub.UpdateFeature(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Feature, bool]:
        request = GetFeatureRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetFeature(request)
            return Feature(response.feature, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteFeatureRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteFeature(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Feature], bool]:
        request = ListFeaturesRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListFeatures(request)
            return [Feature(item, self) for item in response.features.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


