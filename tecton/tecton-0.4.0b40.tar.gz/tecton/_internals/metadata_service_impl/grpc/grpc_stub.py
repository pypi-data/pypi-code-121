import collections

try:
    import grpc
except ImportError:
    raise ImportError("Please install grpcio")

from google.protobuf.empty_pb2 import Empty

from tecton_spark import conf

from tecton._internals.metadata_service_impl import base_stub
from tecton._internals.metadata_service_impl import error_lib
from tecton._internals.metadata_service_impl import request_lib
from tecton_proto.metadataservice import metadata_service_pb2
from collections import defaultdict
from tecton._internals.metadata_service_impl.response import MDSResponse


def _get_host_port() -> str:
    return conf.get_or_raise("METADATA_SERVICE")


class MetadataUnaryUnaryWrapper(object):
    """
    Adding headers from server based on this
    https://github.com/grpc/grpc/blob/master/src/python/grpcio/grpc/_interceptor.py
    """

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, request):
        response_proto, call = self.fn.with_call(request=request)
        return MDSResponse(response_proto, defaultdict(str, dict(call.initial_metadata())))


class MetadataServiceStub(base_stub.BaseStub):
    # Due to https://github.com/stackb/rules_proto/issues/113 generating GRPC
    # classes using protoc is not working. This is manually recreating what
    # protoc does for the client side of GRPC services. It only supports unary-unary.
    # If anything else is needed hopefully that bug has been fixed.
    def __init__(self, channel):
        service_descriptor = metadata_service_pb2.DESCRIPTOR.services_by_name["MetadataService"]
        for method in service_descriptor.methods:
            if method.input_type.name == "Empty":
                request_serializer = Empty.SerializeToString
            else:
                request_serializer = getattr(metadata_service_pb2, method.input_type.name).SerializeToString
            if method.output_type.name == "Empty":
                response_deserializer = Empty.FromString
            else:
                response_deserializer = getattr(metadata_service_pb2, method.output_type.name).FromString
            fn = channel.unary_unary(
                f"/{service_descriptor.full_name}/{method.name}",
                request_serializer=request_serializer,
                response_deserializer=response_deserializer,
            )
            self._channel = channel
            setattr(self, method.name, MetadataUnaryUnaryWrapper(fn))

    def close(self):
        self._channel.close()


class _ClientCallDetails(
    collections.namedtuple("_ClientCallDetails", ("method", "timeout", "metadata", "credentials")),
    grpc.ClientCallDetails,
):
    pass


class MetadataServiceInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.StreamUnaryClientInterceptor):
    """
    Adding headers based on an a example in
    https://github.com/grpc/grpc/blob/master/examples/python/interceptors/headers/header_manipulator_client_interceptor.py
    """

    def __init__(self):
        pass

    @staticmethod
    def _intercept_call(continuation, client_call_details, request_or_iterator):
        metadata = [(k, v) for k, v in request_lib.request_headers().items()]

        client_call_details = _ClientCallDetails(
            client_call_details.method, client_call_details.timeout, metadata, client_call_details.credentials
        )

        response = continuation(client_call_details, request_or_iterator)

        e = response.exception()
        if not e:
            return response

        if isinstance(e, grpc.RpcError):
            error_lib.raise_for_grpc_status(
                status_code=e.code().value[0], details=e.details(), host_url=_get_host_port()
            )

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        return self._intercept_call(continuation, client_call_details, request_iterator)
