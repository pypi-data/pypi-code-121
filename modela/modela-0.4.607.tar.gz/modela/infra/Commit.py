import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import Commit as MDCommit
from github.com.metaprov.modelaapi.services.commit.v1.commit_pb2_grpc import CommitServiceStub
from github.com.metaprov.modelaapi.services.commit.v1.commit_pb2 import CreateCommitRequest, \
    UpdateCommitRequest, \
    DeleteCommitRequest, GetCommitRequest, ListCommitsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Commit(Resource):
    def __init__(self, item: MDCommit = MDCommit(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class CommitClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: CommitServiceStub = stub

    def create(self, commit: Commit) -> bool:
        request = CreateCommitRequest()
        request.commit.CopyFrom(commit.raw_message)
        try:
            response = self.__stub.CreateCommit(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, commit: Commit) -> bool:
        request = UpdateCommitRequest()
        request.commit.CopyFrom(commit.raw_message)
        try:
            self.__stub.UpdateCommit(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Commit, bool]:
        request = GetCommitRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetCommit(request)
            return Commit(response.commit, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteCommitRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteCommit(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Commit], bool]:
        request = ListCommitsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListCommits(request)
            return [Commit(item, self) for item in response.commits.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


