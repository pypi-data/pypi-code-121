import asyncio
import json
import time

import grpc
from google.protobuf import json_format

from github.com.metaprov.modelaapi.pkg.apis.inference.v1alpha1.generated_pb2 import Predictor as MDPredictor
from github.com.metaprov.modelaapi.services.grpcinferenceservice.v1.grpcinferenceservice_pb2 import \
    PredictResultLineItem
from github.com.metaprov.modelaapi.services.predictor.v1.predictor_pb2_grpc import PredictorServiceStub
from github.com.metaprov.modelaapi.services.predictor.v1.predictor_pb2 import CreatePredictorRequest, \
    UpdatePredictorRequest, \
    DeletePredictorRequest, GetPredictorRequest, ListPredictorsRequest, PredictOneRequest

from modela.common import ObjectReference
from modela.Resource import Resource
from modela.ModelaException import ModelaException, ResourceNotFoundException
from typing import List, Union

from modela.inference.InferenceService import InferenceService
from modela.inference.common import AccessType
from modela.inference.models import ModelDeploymentSpec, PredictorSpec, PredictorStatus, PredictionResult, AutoScaling
from modela.infra.ServingSite import ServingSite
from modela.infra.models import Workload
from modela.training.Model import Model


class Predictor(Resource):
    def __init__(self, item: MDPredictor = MDPredictor(), client=None, namespace="", name="",
                 version=Resource.DefaultVersion,
                 serving_site: Union[ObjectReference, ServingSite, str] = "default-serving-site",
                 model: Union[Model, str] = None,
                 models: List[ModelDeploymentSpec] = None,
                 port: int = 3000,
                 path: str = None,
                 access_type: AccessType = None,
                 replicas: int = 0,
                 autoscale: AutoScaling = None,
                 workload: Workload = None):
        """

        :param client: The Predictor client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param version: The version of the resource.
        :param serving_site: The object reference, Serving Site object, or name under the tenant of the resource for which the
            predictor will be deployed under.
        :param model: The Model object or name that the predictor will serve predictions for. This parameter
            will instantiate the predictor with a singe default deployment specification for the model.
        :param models: The list of model deployment specifications that will be applied to the predictor.
        :param port: The port of the predictor, which if applicable will expose the service internally or externally.
        :param path: The path that the predictor will expose a service on. If this parameter is not specified, then
            a path will be generated based on the access type and predictor name.
        :param access_type: The access type of the Predictor. See https://www.modela.ai/docs/docs/serving/production/
            for documentation on how different access types expose the Predictor service
        :param replicas: The amount of replicas for the predictor, which if greater than zero will serve the prediction
            service on multiple pods.
        :param autoscale: If set to true, the predictor's deployment will scale based on the amount of incoming traffic
            to the service.
        :param workload: The workload specification which determines the resources which will be allocated to the
            prediction service.
        """
        self.default_resource = False
        super().__init__(item, client, namespace=namespace, name=name, version=version)

        spec = self.spec
        if type(serving_site) == ServingSite:
            serving_site = serving_site.reference
        elif type(serving_site) == str:
            serving_site = ObjectReference(Namespace=client.modela.tenant, Name=serving_site)

        if model is not None:
            if type(model) == Model:
                model = model.name
            self.spec.Models = [ModelDeploymentSpec(ModelName=model)]
        else:
            self.spec.Models = models

        if self.default_resource:
            self.spec.ServingsiteRef = serving_site
            if port is not None:
                spec.Port = port

            if path is not None:
                spec.Path = path

            if access_type is not None:
                spec.AccessType = access_type.value

        if replicas > 0:
            spec.Replicas = replicas

        if workload is not None:
            spec.Resources = workload

        if autoscale is not None:
            spec.AutoScaling = autoscale

    @property
    def spec(self) -> PredictorSpec:
        return PredictorSpec().copy_from(self._object.spec)

    @property
    def status(self) -> PredictorStatus:
        return PredictorStatus().copy_from(self._object.status)

    def default(self):
        self.default_resource = True
        PredictorSpec().apply_config(self._object.spec)

    @property
    def model(self) -> Model:
        """ Get the model associated with the Predictor """
        self.ensure_client_repository()
        return self._client.modela.Model(self.namespace, self.spec.Models[0].ModelName)

    async def wait_until_ready(self):
        """ Block until the predictor service is ready to accept prediction requests. """
        payload = self.model.test_prediction
        while True:
            try:
                self.predict(payload)
            except ResourceNotFoundException:
                await asyncio.sleep(1 / 5)
                continue

            return

    def predict(self, predictions: Union[str, dict, List[dict]]) -> List[PredictionResult]:
        """
        Send a batch prediction request

        :param predictions: The JSON payload or dictionary(s) that contain each features name and their input value
        """
        self.ensure_client_repository()
        if type(predictions) == dict:
            predictions = json.dumps([predictions])
        elif type(predictions) == list:
            predictions = json.dumps(predictions)

        return self._client.predict(self.namespace, self.name, "", predictions)

    def connect(self, node_ip="", port_forward=False, tls_cert: str = None) -> InferenceService:
        """
        Connect attempts to make a connection to the gRPC inference service client associated with the Predictor.

        Note that if the Predictor access type is ClusterIP, the SDK will attempt to connect to the Predictor service
        using its cluster-internal DNS (i.e. my-predictor.default-serving-site.svc.cluster.local), of which can
        only be accessed by containers running on the cluster.

        :param node_ip: If the Predictor's access type is of type NodePort, a Kubernetes node IP of the cluster
            hosting the current Modela instance must be provided. This IP can be found by executing the command
            `kubectl get nodes -o wide`
        :param port_forward: If enabled, the SDK will attempt to port forward the Predictor service using kubectl. Kubectl
            must be installed and must be connected to the cluster with the Predictor is running on.
        :param tls_cert: If the Predictor's access type is Ingress, the TLS certificate of the Predictor's Serving Site
           must be provided.
        :return: The InferenceService client connected to the prediction proxy service
        """
        assert node_ip != "" or self.spec.AccessType != AccessType.NodePort

        if port_forward:
            return InferenceService(port_forward=True,
                                    service_namespace=self.spec.ServingsiteRef.Name,
                                    service_name=self.name)

        if self.spec.AccessType == AccessType.NodePort or self.spec.AccessType == AccessType.LoadBalancer:
            return InferenceService((node_ip if node_ip != "" else self.spec.Path), self.spec.NodePort)
        elif self.spec.AccessType == AccessType.Ingress:
            return InferenceService(self.spec.Path, tls_cert=tls_cert)
        elif self.spec.AccessType == AccessType.ClusterIP:
            return InferenceService(self.spec.Path, self.spec.Port)


class PredictorClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: PredictorServiceStub = stub

    def create(self, predictor: Predictor) -> bool:
        request = CreatePredictorRequest()
        request.predictor.CopyFrom(predictor.raw_message)
        try:
            response = self.__stub.CreatePredictor(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, predictor: Predictor) -> bool:
        request = UpdatePredictorRequest()
        request.predictor.CopyFrom(predictor.raw_message)
        try:
            self.__stub.UpdatePredictor(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Predictor:
        request = GetPredictorRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetPredictor(request)
            return Predictor(response.predictor, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)

    def delete(self, namespace: str, name: str) -> bool:
        request = DeletePredictorRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeletePredictor(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str, labels: dict = None) -> List[Predictor]:
        request = ListPredictorsRequest()
        request.namespace = namespace
        if labels is not None:
            request.labels.update(labels)

        try:
            response = self.__stub.ListPredictors(request)
            return [Predictor(item, self) for item in response.predictors.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)

    def predict(self, namespace: str, name: str, fields: str, values: str) -> List[PredictionResult]:
        request = PredictOneRequest()
        request.namespace = namespace
        request.name = name
        request.fields = fields
        request.values = values

        try:
            response = self.__stub.PredictOne(request)
            output = json.loads(response.label)
            print(output)
            return [PredictionResult().from_dict(item) for item in output["items"]]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False
