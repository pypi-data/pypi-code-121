import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import FeaturePipeline as MDFeaturePipeline
from github.com.metaprov.modelaapi.services.featurepipeline.v1.featurepipeline_pb2_grpc import FeaturePipelineServiceStub
from github.com.metaprov.modelaapi.services.featurepipeline.v1.featurepipeline_pb2 import CreateFeaturePipelineRequest, \
    UpdateFeaturePipelineRequest, \
    DeleteFeaturePipelineRequest, GetFeaturePipelineRequest, ListFeaturePipelineRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class FeaturePipeline(Resource):
    def __init__(self, item: MDFeaturePipeline = MDFeaturePipeline(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class FeaturePipelineClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: FeaturePipelineServiceStub = stub

    def create(self, featurepipeline: FeaturePipeline) -> bool:
        request = CreateFeaturePipelineRequest()
        request.featurepipeline.CopyFrom(featurepipeline.raw_message)
        try:
            response = self.__stub.CreateFeaturePipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, featurepipeline: FeaturePipeline) -> bool:
        request = UpdateFeaturePipelineRequest()
        request.featurepipeline.CopyFrom(featurepipeline.raw_message)
        try:
            self.__stub.UpdateFeaturePipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[FeaturePipeline, bool]:
        request = GetFeaturePipelineRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetFeaturePipeline(request)
            return FeaturePipeline(response.featurepipeline, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteFeaturePipelineRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteFeaturePipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[FeaturePipeline], bool]:
        request = ListFeaturePipelineRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListFeaturePipelines(request)
            return [FeaturePipeline(item, self) for item in response.featurepipelines.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


