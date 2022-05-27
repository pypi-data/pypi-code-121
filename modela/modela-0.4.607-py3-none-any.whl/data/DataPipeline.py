import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import DataPipeline as MDDataPipeline
from github.com.metaprov.modelaapi.services.datapipeline.v1.datapipeline_pb2_grpc import DataPipelineServiceStub
from github.com.metaprov.modelaapi.services.datapipeline.v1.datapipeline_pb2 import CreateDataPipelineRequest, \
    UpdateDataPipelineRequest, \
    DeleteDataPipelineRequest, GetDataPipelineRequest, ListDataPipelinesRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class DataPipeline(Resource):
    def __init__(self, item: MDDataPipeline = MDDataPipeline(), client=None, namespace="", name="", version=Resource.DefaultVersion):
        super().__init__(item, client, namespace=namespace, name=name, version=version)


class DataPipelineClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: DataPipelineServiceStub = stub

    def create(self, datapipeline: DataPipeline) -> bool:
        request = CreateDataPipelineRequest()
        request.datapipeline.CopyFrom(datapipeline.raw_message)
        try:
            response = self.__stub.CreateDataPipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, datapipeline: DataPipeline) -> bool:
        request = UpdateDataPipelineRequest()
        request.datapipeline.CopyFrom(datapipeline.raw_message)
        try:
            self.__stub.UpdateDataPipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[DataPipeline, bool]:
        request = GetDataPipelineRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetDataPipeline(request)
            return DataPipeline(response.datapipeline, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteDataPipelineRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteDataPipeline(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[DataPipeline], bool]:
        request = ListDataPipelinesRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListDataPipelines(request)
            return [DataPipeline(item, self) for item in response.datapipelines.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


