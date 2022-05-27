import grpc # type: ignore

from grpc import (  # type: ignore
    UnaryUnaryClientInterceptor,
    UnaryStreamClientInterceptor,
    StreamUnaryClientInterceptor,
    StreamStreamClientInterceptor
)

from github.com.metaprov.modelaapi.services.grpcinferenceservice.v1 import grpcinferenceservice_pb2
from github.com.metaprov.modelaapi.services.grpcinferenceservice.v1 import grpcinferenceservice_pb2_grpc

from typing import Dict, Optional, Union, List

SERVER_ADDRESS = '0.0.0.0'
PORT = 8080


from dataclasses import dataclass

########################################################
# Server data
########################################################

@dataclass
class ServerInfo:
    name: str

@dataclass
class Metric:
    name: str
    value: float


@dataclass
class ModelInfo:
    name: str
    version: str
    product: str
    trainingMetrics: List[Metric]
    trainingScore: float
    status: str
    canary: bool
    shadow: bool
    traffic: float
    filter:str
    rank:int
    logPath: str
    p95: float
    p99: float
    lastPrediction: int
    dailyPredictionAvg: float

@dataclass
class ColumnInfo:
    name: str
    type: str
    datasetMin: float
    datasetMean: float
    datasetStdDev: float
    datasetMax: float


@dataclass
class SchemaInfo:
    columns: List[ColumnInfo]

@dataclass
class PredictorInfo:
    name: str
    task: str
    models: List[ModelInfo]
    schema: SchemaInfo

@dataclass
class OnePrediction:
    payload:str

@dataclass
class Predictions:
    payload:str # result as json
    items: List[OnePrediction]


#######################################################
# Model data
#######################################################


class ModelaGrpcClient(object):
    def __init__(self,
                 host,
                 port=3000,
                 interceptors: Optional[List[Union[
                     UnaryUnaryClientInterceptor,
                     UnaryStreamClientInterceptor,
                     StreamUnaryClientInterceptor,
                     StreamStreamClientInterceptor]]] = None
                 ):
        """Initializer.
           Creates a gRPC channel for connecting to the server.
           Adds the channel to the generated client stub.

        Arguments:
            None.

        Returns:
            None.
        """
        self._channel = grpc.insecure_channel(f'{host}:{port}')

        if interceptors:
            self._channel = grpc.intercept_channel(  # type: ignore
                self._channel, *interceptors)

        self._stub = grpcinferenceservice_pb2_grpc.GRPCInferenceServiceStub(self._channel)

    def close(self):
        """Closes Dapr runtime gRPC channel."""
        if self._channel:
            self._channel.close()

    def __del__(self):
        self.close()

    def __enter__(self) -> 'ModelaGrpcClient':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def is_alive(self) -> bool:
        """Check if the service is alive

        Arguments:
           None

        Returns:
           bool; True if the predictor is alive
        """
        request = grpcinferenceservice_pb2.ServiceLiveRequest()
        try:
            response = self._stub.ServiceLive(request)
            return response.live
        except grpc.RpcError as err:
            print(err.details())  # pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value))  # pylint: disable=no-member
            return False

    def is_ready(self) -> bool:
        """Check if the service is ready

        Arguments:
             None

        Returns:
            bool; True if the predictor is alive
        """
        request = grpcinferenceservice_pb2.ServiceReadyRequest()
        try:
            response = self._stub.ServerReady(request)
            return response.ready
        except grpc.RpcError as err:
            print(err.details())  # pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value))  # pylint: disable=no-member
            return False

    def model_ready(self,name:str,version:str) -> bool:
        """Check if a specific model is ready

        Arguments:
             None

        Returns:
            bool; True if the predictor is alive
        """

        request = grpcinferenceservice_pb2.ModelReadyRequest()
        request.name    = name
        request.version = version
        try:
            response = self._stub.ModelReady(request)
            return response.ready
        except grpc.RpcError as err:
            print(err.details())  # pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value))  # pylint: disable=no-member
            return False

    def server_metadata(self) -> ServerInfo:
        """Answer the server metadata info

        Arguments:
             None

        Returns:
            bool; True if the predictor is alive
        """

        request = grpcinferenceservice_pb2.ServerMetadataRequest()
        try:
            response = self._stub.ServerMetadata(request)
            return response.ready
        except grpc.RpcError as err:
            print(err.details())  # pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value))  # pylint: disable=no-member


    def model_metadata(self,name:str,version:str) -> ModelInfo:
        request = grpcinferenceservice_pb2.ModelMetadataRequest()
        request.name = name
        request.version = version
        try:
            response = self._stub.ModelMetadata(request)
            return response.ready
        except grpc.RpcError as err:
            print(err.details())  # pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value))  # pylint: disable=no-member
            return False


    def get_predictor(self) -> PredictorInfo:
        request = grpcinferenceservice_pb2.GetPredictorRequest()
        try:
            response = self._stub.GetPredictor(request)
            return response.item
        except grpc.RpcError as err:
            print(err.details())  # pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value))  # pylint: disable=no-member
            raise err

    def get_model(self,predictor,name) -> ModelInfo:
        """Answer the model information

        Arguments:
             name - the name of the model

        Returns:
            bool; True if the predictor is alive
        """

        request = grpcinferenceservice_pb2.GetModelRequest()
        request.predictorName = predictor
        request.name          = name
        try:
            response = self._stub.GetModel(request)
            return response.item
        except grpc.RpcError as err:
            print(err.details())  # pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value))  # pylint: disable=no-member
            raise err


    def predict(self,
                payload:str,
                name="",
                validate=False,
                explain=False,
                format="json",
                labeled=False,
                metrics=None) -> Predictions:
        request = grpcinferenceservice_pb2.PredictRequest()
        request.name      = name
        request.validate  = validate
        request.explain   = explain
        request.format    = format
        request.payload   = payload
        request.labeled   = labeled
        request.metrics.extend(metrics)

        try:
            response = self._stub.Predict(request)
            return response.items
        except grpc.RpcError as err:
            print(err.details())  # pylint: disable=no-member
            print('{}, {}'.format(err.code().name, err.code().value))  # pylint: disable=no-member
            raise err