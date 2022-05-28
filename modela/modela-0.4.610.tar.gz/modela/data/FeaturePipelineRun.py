import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import FeaturePipelineRun as MDFeaturePipelineRun
from github.com.metaprov.modelaapi.services.featurepipelinerun.v1.featurepipelinerun_pb2_grpc import FeaturePipelineRunServiceStub
from github.com.metaprov.modelaapi.services.featurepipelinerun.v1.featurepipelinerun_pb2 import CreateFeaturePipelineRunRequest, \
    UpdateFeaturePipelineRunRequest, \
    DeleteFeaturePipelineRunRequest, GetFeaturePipelineRunRequest, ListFeaturePipelineRunRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class FeaturePipelineRun(Resource):
    def __init__(self, item: MDFeaturePipelineRun = MDFeaturePipelineRun(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class FeaturePipelineRunClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: FeaturePipelineRunServiceStub = stub

    def create(self, featurepipelinerun: FeaturePipelineRun) -> bool:
        request = CreateFeaturePipelineRunRequest()
        request.featurepipelinerun.CopyFrom(featurepipelinerun.raw_message)
        try:
            response = self.__stub.CreateFeaturePipelineRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, featurepipelinerun: FeaturePipelineRun) -> bool:
        request = UpdateFeaturePipelineRunRequest()
        request.featurepipelinerun.CopyFrom(featurepipelinerun.raw_message)
        try:
            self.__stub.UpdateFeaturePipelineRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[FeaturePipelineRun, bool]:
        request = GetFeaturePipelineRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetFeaturePipelineRun(request)
            return FeaturePipelineRun(response.featurepipelinerun, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteFeaturePipelineRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteFeaturePipelineRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[FeaturePipelineRun], bool]:
        request = ListFeaturePipelineRunRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListFeaturePipelineRuns(request)
            return [FeaturePipelineRun(item, self) for item in response.featurepipelineruns.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


