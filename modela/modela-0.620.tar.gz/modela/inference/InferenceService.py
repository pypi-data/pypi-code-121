import hashlib
import subprocess
import time
from contextlib import closing
import socket
from typing import List

import grpc
from github.com.metaprov.modelaapi.services.grpcinferenceservice.v1 import grpcinferenceservice_pb2_grpc
from github.com.metaprov.modelaapi.services.grpcinferenceservice.v1.grpcinferenceservice_pb2 import PredictRequest
from github.com.metaprov.modelaapi.services.grpcinferenceservice.v1.grpcinferenceservice_pb2_grpc import \
    GRPCInferenceServiceStub

from modela.ModelaException import ModelaException
from modela.inference.models import PredictionResult


class InferenceService:
    """
    The InferenceService class represents a connection to a gRPC service that exposes the GRPCInferenceService API.
    This API exposes methods to make prediction requests and view information about the current status of the
    prediction proxy.
    """

    def __init__(self, host="localhost", port=None, tls_cert=None, port_forward=False, service_name="", service_namespace=""):
        """
        Connect to the gRPC service.

        :param host: The DNS name or IP that hosts the service.
        :param port: The port which exposes the service.
        :param tls_cert: The TLS certificate of the connection, if connecting through ingress. The Secret containing the
            public key of the ingress can be found in the namespace of the Serving Site that hosts the service.
        """
        if port_forward:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.bind(('', 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                port = s.getsockname()[1]

            self.pf_process = subprocess.Popen("kubectl port-forward svc/%s %d:8080 -n %s" %
                                               (service_name, port, service_namespace),
                                               shell=True, stderr=subprocess.STDOUT)

            time.sleep(1/4)
            tls_cert, host = None, "localhost"

        if tls_cert:
            with open(tls_cert, 'rb') as f:
                credentials = grpc.ssl_channel_credentials(f.read())

            self._channel = grpc.secure_channel(f'{host}', credentials)
        else:
            if port != None:
                self._channel = grpc.insecure_channel(f'{host}:{port}')
            else:
                self._channel = grpc.insecure_channel(f'{host}')

        self._stub = grpcinferenceservice_pb2_grpc.GRPCInferenceServiceStub(self._channel)

    def close(self):
        """Closes Dapr runtime gRPC channel."""
        if self._channel:
            self._channel.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if hasattr(self, 'pf_process'):
            self.pf_process.kill()

        self.close()

    def predict(self,
                payload: str,
                validate: bool = True,
                explain: bool = False,
                format: str = "json",
                labeled: bool = False,
                metrics: List[str] = []) -> List[PredictionResult]:
        request = PredictRequest(validate=validate, explain=explain, format=format,
                                 payload=payload, labeled=labeled)
        request.metrics.extend(metrics)
        try:
            response = self._stub.Predict(request)
            return [PredictionResult().copy_from(item) for item in response.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
