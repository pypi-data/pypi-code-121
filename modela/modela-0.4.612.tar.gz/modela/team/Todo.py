import grpc
from github.com.metaprov.modelaapi.pkg.apis.team.v1alpha1.generated_pb2 import Todo as MDTodo
from github.com.metaprov.modelaapi.services.todo.v1.todo_pb2_grpc import TodoServiceStub
from github.com.metaprov.modelaapi.services.todo.v1.todo_pb2 import CreateTodoRequest, \
    UpdateTodoRequest, \
    DeleteTodoRequest, GetTodoRequest, ListTodosRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Todo(Resource):
    def __init__(self, item: MDTodo = MDTodo(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class TodoClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: TodoServiceStub = stub

    def create(self, todo: Todo) -> bool:
        request = CreateTodoRequest()
        request.todo.CopyFrom(todo.raw_message)
        try:
            response = self.__stub.CreateTodo(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, todo: Todo) -> bool:
        request = UpdateTodoRequest()
        request.todo.CopyFrom(todo.raw_message)
        try:
            self.__stub.UpdateTodo(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Todo, bool]:
        request = GetTodoRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetTodo(request)
            return Todo(response.todo, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteTodoRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteTodo(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Todo], bool]:
        request = ListTodosRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListTodos(request)
            return [Todo(item, self) for item in response.todos.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


