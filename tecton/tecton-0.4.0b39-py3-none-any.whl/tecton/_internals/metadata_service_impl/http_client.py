import base64
from collections import defaultdict
from typing import Any
from typing import Tuple

import requests
from google.protobuf.empty_pb2 import Empty

from tecton._internals.metadata_service_impl import base_stub
from tecton._internals.metadata_service_impl import error_lib
from tecton._internals.metadata_service_impl import request_lib
from tecton._internals.metadata_service_impl.response import MDSResponse
from tecton_proto.metadataservice import metadata_service_pb2
from tecton_spark.logger import get_logger

logger = get_logger("metadata_service")

requests_session = requests.Session()


class PureHTTPStub(base_stub.BaseStub):
    def __init__(self):
        """
        PureHTTPStub mimics the interface exposed by a gRPC client for MetadataService.
        Callers can invoke a method like stub.GetFeatureView and it's transformed for an HTTP
        request using _InternalHTTPStub in the __getattr__ method below.
        """
        self.stub_obj = _InternalHTTPStub()

    def __getattr__(self, method_name):
        """
        Transforms methods called directly on PureHTTPStub to _InternalHTTPStub requests.
        E.g. PureHTTPStub::SomeMethod(request) is transformed to _InternalHTTPStub::execute('SomeMethod', request).

        An AttributeError is raised if the method invoked does not match a MetadataService RPC method.
        """
        methods = [m.name for m in metadata_service_pb2.DESCRIPTOR.services_by_name["MetadataService"].methods]
        if method_name not in methods:
            raise AttributeError("Nonexistent MetadataService method: " + method_name)

        def method(request):
            return self.stub_obj.execute(method_name, request)

        return method

    def close(self):
        pass


class _InternalHTTPStub:
    def __init__(self):
        pass

    def execute(self, method: str, request):
        """
        :param method: gRPC method name.
        :param request: Request proto.

        :return: Response proto.
        """
        json_request = {}
        json_request["method"] = f"/tecton_proto.metadataservice.MetadataService/{method}"
        json_request["metadata"] = request_lib.request_headers()
        request_serializer, response_deserializer = self._get_serializers(method)

        json_request["request"] = base64.encodebytes(request_serializer(request)).decode("utf-8")

        request_url = request_lib.request_url()
        response = requests_session.post(request_url, json=json_request, timeout=300.0)
        response.raise_for_status()
        body = response.json()

        code = body["status"]["code"]
        if code != error_lib.gRPCStatus.OK.value:
            details = body["status"]["detail"]
            error_lib.raise_for_grpc_status(code, details, request_url)

        response_bytes = base64.decodebytes(body["response"].encode("utf-8"))
        response_proto = response_deserializer(response_bytes)
        metadata = body.get("metadata", "")
        return MDSResponse(response_proto, defaultdict(str, metadata))

    def _get_serializers(self, method_name) -> Tuple[Any, Any]:
        """
        :param method_name: gRPC method name, e.g. GetFeatureView.

        :return: A tuple of request serializer and request deserializer objects.
        """

        service_descriptor = metadata_service_pb2.DESCRIPTOR.services_by_name["MetadataService"]
        request_serializer = None
        response_deserializer = None
        for method in service_descriptor.methods:
            if method.name != method_name:
                continue

            if method.input_type.name == "Empty":
                request_serializer = Empty.SerializeToString
            else:
                request_serializer = getattr(metadata_service_pb2, method.input_type.name).SerializeToString
            if method.output_type.name == "Empty":
                response_deserializer = Empty.FromString
            else:
                response_deserializer = getattr(metadata_service_pb2, method.output_type.name).FromString

        assert (
            request_serializer is not None and response_deserializer is not None
        ), f"No request_serializer or response_deserializer match for {method_name}"
        return request_serializer, response_deserializer
