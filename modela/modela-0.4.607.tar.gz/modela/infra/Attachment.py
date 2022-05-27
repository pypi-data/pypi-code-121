import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import Attachment as MDAttachment
from github.com.metaprov.modelaapi.services.attachment.v1.attachment_pb2_grpc import AttachmentServiceStub
from github.com.metaprov.modelaapi.services.attachment.v1.attachment_pb2 import CreateAttachmentRequest, \
    UpdateAttachmentRequest, \
    DeleteAttachmentRequest, GetAttachmentRequest, ListAttachmentsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union


class Attachment(Resource):
    def __init__(self, item: MDAttachment = MDAttachment(), client=None, namespace="", name=""):
        super().__init__(item, client, namespace=namespace, name=name)


class AttachmentClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: AttachmentServiceStub = stub

    def create(self, attachment: Attachment) -> bool:
        request = CreateAttachmentRequest()
        request.attachment.CopyFrom(attachment.raw_message)
        try:
            response = self.__stub.CreateAttachment(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, attachment: Attachment) -> bool:
        request = UpdateAttachmentRequest()
        request.attachment.CopyFrom(attachment.raw_message)
        try:
            self.__stub.UpdateAttachment(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[Attachment, bool]:
        request = GetAttachmentRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetAttachment(request)
            return Attachment(response.attachment, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteAttachmentRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteAttachment(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[Attachment], bool]:
        request = ListAttachmentsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListAttachments(request)
            return [Attachment(item, self) for item in response.attachments.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


