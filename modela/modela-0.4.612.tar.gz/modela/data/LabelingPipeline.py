import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import LabelingPipeline as MDLabelingPipeline
from github.com.metaprov.modelaapi.services.labelingpipeline.v1.labelingpipeline_pb2_grpc import LabelingPipelineServiceStub
from github.com.metaprov.modelaapi.services.labelingpipeline.v1.labelingpipeline_pb2 import CreateLabelingPipelineRequest, \
    UpdateLabelingPipelineRequest, \
    DeleteLabelingPipelineRequest, GetLabelingPipelineRequest, ListLabelingPipelineRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class LabelingPipeline(Resource):
    def __init__(self, item: MDLabelingPipeline = MDLabelingPipeline(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class LabelingPipelineClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: LabelingPipelineServiceStub = stub

    def create(self, labelingpipeline: LabelingPipeline) -> bool:
        request = CreateLabelingPipelineRequest()
        request.labelingpipeline.CopyFrom(labelingpipeline.raw_message)
        try:
            response = self.__stub.CreateLabelingPipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, labelingpipeline: LabelingPipeline) -> bool:
        request = UpdateLabelingPipelineRequest()
        request.labelingpipeline.CopyFrom(labelingpipeline.raw_message)
        try:
            self.__stub.UpdateLabelingPipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[LabelingPipeline, bool]:
        request = GetLabelingPipelineRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetLabelingPipeline(request)
            return LabelingPipeline(response.labelingpipeline, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteLabelingPipelineRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteLabelingPipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[LabelingPipeline], bool]:
        request = ListLabelingPipelineRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListLabelingPipelines(request)
            return [LabelingPipeline(item, self) for item in response.labelingpipelines.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


