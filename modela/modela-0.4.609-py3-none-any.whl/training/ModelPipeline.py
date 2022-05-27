import grpc
from github.com.metaprov.modelaapi.pkg.apis.training.v1alpha1.generated_pb2 import ModelPipeline as MDModelPipeline
from github.com.metaprov.modelaapi.services.modelpipeline.v1.modelpipeline_pb2_grpc import ModelPipelineServiceStub
from github.com.metaprov.modelaapi.services.modelpipeline.v1.modelpipeline_pb2 import CreateModelPipelineRequest, \
    UpdateModelPipelineRequest, \
    DeleteModelPipelineRequest, GetModelPipelineRequest, ListModelPipelinesRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class ModelPipeline(Resource):
    def __init__(self, item: MDModelPipeline = MDModelPipeline(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class ModelPipelineClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: ModelPipelineServiceStub = stub

    def create(self, modelpipeline: ModelPipeline) -> bool:
        request = CreateModelPipelineRequest()
        request.modelpipeline.CopyFrom(modelpipeline.raw_message)
        try:
            response = self.__stub.CreateModelPipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, modelpipeline: ModelPipeline) -> bool:
        request = UpdateModelPipelineRequest()
        request.modelpipeline.CopyFrom(modelpipeline.raw_message)
        try:
            self.__stub.UpdateModelPipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[ModelPipeline, bool]:
        request = GetModelPipelineRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetModelPipeline(request)
            return ModelPipeline(response.modelpipeline, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteModelPipelineRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteModelPipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[ModelPipeline], bool]:
        request = ListModelPipelinesRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListModelPipelines(request)
            return [ModelPipeline(item, self) for item in response.modelpipelines.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


