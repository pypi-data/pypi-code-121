import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import LabelingPipelineRun as MDLabelingPipelineRun
from github.com.metaprov.modelaapi.services.labelingpipelinerun.v1.labelingpipelinerun_pb2_grpc import LabelingPipelineRunServiceStub
from github.com.metaprov.modelaapi.services.labelingpipelinerun.v1.labelingpipelinerun_pb2 import CreateLabelingPipelineRunRequest, \
    UpdateLabelingPipelineRunRequest, \
    DeleteLabelingPipelineRunRequest, GetLabelingPipelineRunRequest, ListLabelingPipelineRunRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class LabelingPipelineRun(Resource):
    def __init__(self, item: MDLabelingPipelineRun = MDLabelingPipelineRun(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class LabelingPipelineRunClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: LabelingPipelineRunServiceStub = stub

    def create(self, labelingpipelinerun: LabelingPipelineRun) -> bool:
        request = CreateLabelingPipelineRunRequest()
        request.labelingpipelinerun.CopyFrom(labelingpipelinerun.raw_message)
        try:
            response = self.__stub.CreateLabelingPipelineRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, labelingpipelinerun: LabelingPipelineRun) -> bool:
        request = UpdateLabelingPipelineRunRequest()
        request.labelingpipelinerun.CopyFrom(labelingpipelinerun.raw_message)
        try:
            self.__stub.UpdateLabelingPipelineRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[LabelingPipelineRun, bool]:
        request = GetLabelingPipelineRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetLabelingPipelineRun(request)
            return LabelingPipelineRun(response.labelingpipelinerun, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteLabelingPipelineRunRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteLabelingPipelineRun(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[LabelingPipelineRun], bool]:
        request = ListLabelingPipelineRunRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListLabelingPipelineRuns(request)
            return [LabelingPipelineRun(item, self) for item in response.labelingpipelineruns.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


