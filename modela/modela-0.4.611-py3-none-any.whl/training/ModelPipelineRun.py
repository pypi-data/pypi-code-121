import grpc
from github.com.metaprov.modelaapi.pkg.apis.training.v1alpha1.generated_pb2 import ModelPipelineRun as MDModelPipelineRun
from github.com.metaprov.modelaapi.services.modelpipelinerun.v1.modelpipelinerun_pb2_grpc import ModelPipelineRunServiceStub
from github.com.metaprov.modelaapi.services.modelpipelinerun.v1.modelpipelinerun_pb2 import CreateModelPipelineRunRequest, \
    UpdateModelPipelineRunRequest, \
    DeleteModelPipelineRunRequest, GetModelPipelineRunRequest, ListModelPipelineRunsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class ModelPipelineRun(Resource):
    def __init__(self, item: MDModelPipelineRun = MDModelPipelineRun(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class ModelPipelineRunClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: ModelPipelineRunServiceStub = stub

    def create(self, modelpipelinerun: ModelPipelineRun) -> bool:
        request = CreateModelPipelineRunRequest()
        request.modelpipelinerun.CopyFrom(modelpipelinerun.raw_message)
        try:
            response = self.__stub.CreateModelPipelineRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, modelpipelinerun: ModelPipelineRun) -> bool:
        request = UpdateModelPipelineRunRequest()
        request.modelpipelinerun.CopyFrom(modelpipelinerun.raw_message)
        try:
            self.__stub.UpdateModelPipelineRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[ModelPipelineRun, bool]:
        request = GetModelPipelineRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetModelPipelineRun(request)
            return ModelPipelineRun(response.modelpipelinerun, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteModelPipelineRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteModelPipelineRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[ModelPipelineRun], bool]:
        request = ListModelPipelineRunsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListModelPipelineRuns(request)
            return [ModelPipelineRun(item, self) for item in response.modelpipelineruns.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


