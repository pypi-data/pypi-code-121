import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import Account as MDAccount
from github.com.metaprov.modelaapi.services.account.v1.account_pb2_grpc import AccountServiceStub
from github.com.metaprov.modelaapi.services.account.v1.account_pb2 import CreateAccountRequest, \
    UpdateAccountRequest, \
    DeleteAccountRequest, GetAccountRequest, ListAccountsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Account(Resource):
    def __init__(self, item: MDAccount = MDAccount(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class AccountClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: AccountServiceStub = stub

    def create(self, account: Account) -> bool:
        request = CreateAccountRequest()
        request.account.CopyFrom(account.raw_message)
        try:
            response = self.__stub.CreateAccount(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, account: Account) -> bool:
        request = UpdateAccountRequest()
        request.account.CopyFrom(account.raw_message)
        try:
            self.__stub.UpdateAccount(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Account, bool]:
        request = GetAccountRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetAccount(request)
            return Account(response.account, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteAccountRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteAccount(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Account], bool]:
        request = ListAccountsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListAccounts(request)
            return [Account(item, self) for item in response.accounts.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


