import asyncio
import os
import time

import grpc
import pandas
from github.com.metaprov.modelaapi.pkg.apis.training.v1alpha1.generated_pb2 import \
    ModelAutobuilder as MDModelAutobuilder
from github.com.metaprov.modelaapi.services.modelautobuilder.v1.modelautobuilder_pb2_grpc import \
    ModelAutobuilderServiceStub
from github.com.metaprov.modelaapi.services.modelautobuilder.v1.modelautobuilder_pb2 import \
    CreateModelAutobuilderRequest, \
    UpdateModelAutobuilderRequest, \
    DeleteModelAutobuilderRequest, GetModelAutobuilderRequest, ListModelAutobuildersRequest

from modela.data.Dataset import Dataset
from modela.data.DataSource import DataSource
from modela.inference.DataApp import DataApp
from modela.inference.Predictor import Predictor
from modela.training.Study import Study
from modela.training.models import *
from modela.data.models import SampleSettings
from modela.data.common import *
from modela.infra.VirtualBucket import VirtualBucket
from modela.infra.models import Workload
from modela.infra.Lab import Lab
from modela.infra.ServingSite import ServingSite
from modela.training.common import *
from modela.Resource import Resource
from modela.ModelaException import ModelaException
from modela.common import ObjectReference
from typing import List, Union


class ModelAutobuilder(Resource):
    def __init__(self, item: MDModelAutobuilder = MDModelAutobuilder(), client=None, namespace="", name="",
                 version=Resource.DefaultVersion,
                 lab: Union[ObjectReference, Lab, str] = "default-lab",
                 serving_site: Union[ObjectReference, ServingSite, str] = "default-serving-site",
                 task_type: TaskType = TaskType.BinaryClassification,
                 workload: Workload = Workload("general-large"),
                 bucket: Union[ObjectReference, VirtualBucket, str] = "default-minio-bucket",
                 dataframe: pandas.DataFrame = None,
                 data_file: str = None,
                 data_bytes: bytes = None,
                 target_column: str = None,
                 objective: Metric = Metric.Accuracy,
                 feature_selection: bool = False,
                 feature_engineering: bool = False,
                 max_models: int = 1,
                 max_time: int = 512,
                 trainers: int = 1,
                 predictor_access_type: AccessType = AccessType.ClusterIP,
                 predictor_autoscale: bool = False,
                 create_data_app: bool = False):
        """
        :param client: The Study client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param version: The version of the resource.
        :param lab: The object reference, Lab object, or lab name under the tenant of the resource for which all
            data science workloads will be performed under.
        :param serving_site: The object reference, Serving Site object, or name under the tenant of the resource for which
            the created Predictor will be deployed under.
        :param task_type: The target task type in relation to the data being used.
        :param workload: The workload specification which determines the resources which will be allocated for training
            and serving workloads.
        :param bucket: The bucket which the raw dataset data will be uploaded to.
        :param dataframe: The Pandas Dataframe will be serialized and uploaded to create a new Dataset resource.
        :param data_file: The file path which will be read and uploaded to create a new Dataset resource.
        :param data_bytes: The raw data as bytes that will be uploaded to create a new Dataset resource.
        :param target_column: The target column of the Dataset to be created.
        :param objective: The objective metric to be used when determining the best model from the Study.
        :param feature_selection: If True feature selection will be performed on the Dataset before the model search.
        :param feature_engineering: If True feature engineering will be performed on the Dataset before the model search.
        :param max_models: The maximum number of models to sample before selecting the best model.
        :param max_time: The maximum amount of time in seconds which the model search can run for.
        :param trainers: The number of parallel trainers to allocate during the model search
        :param predictor_access_type: The access type of the Predictor to be created. See https://www.modela.ai/docs/docs/serving/production/
            for documentation on how different access types expose the Predictor service
        :param predictor_autoscale: If true the created Predictor will automatically scale for traffic
        :param create_data_app: If true a Data Application will be created to serve a live model dashboard
        """
        self.default_resource = False
        super().__init__(item, client, namespace=namespace, name=name, version=version)
        if not self.default_resource:  # Ignore the rest of the constructor; MAB is immutable
            return

        spec = self.spec
        if type(lab) == Lab:
            lab = lab.reference
        elif type(lab) == str:
            lab = ObjectReference(Namespace=client.modela.tenant, Name=lab)

        if type(serving_site) == ServingSite:
            serving_site = serving_site.reference
        elif type(serving_site) == str:
            serving_site = ObjectReference(Namespace=client.modela.tenant, Name=serving_site)

        spec.LabRef = lab
        spec.ServingSiteRef = serving_site

        if data_file is not None:
            with open(data_file, 'r') as f:
                data_bytes = f.read()
            data_file = os.path.basename(data_file)
        elif dataframe is not None:
            data_bytes = bytes(dataframe.to_csv(index=False), encoding='utf-8')

        spec.Location = client.modela.FileService.upload_file(data_file or name, data_bytes,
                                                              client.modela.tenant,
                                                              namespace, version, bucket, "datasets", name)

        datasource = client.modela.DataSource(namespace=namespace, name=f"{name}-sdk-autobuilder", version=version,
                                              infer_bytes=data_bytes, target_column=target_column, task_type=task_type,
                                              file_type=FlatFileType.Csv)
        spec.DataSourceSpec = datasource.spec
        spec.DataProductName = namespace
        spec.DataProductVersionName = version
        spec.DatasourceName = name
        spec.DatasetName = name
        spec.Task = task_type
        spec.TargetColumn = target_column

        spec.Resources = workload
        spec.Objective = objective
        spec.FeatureSelection = feature_selection
        spec.FeatureEngineering = feature_engineering
        spec.MaxModels = max_models
        spec.MaxTime = max_time
        spec.Trainers = trainers
        spec.AccessMethod = predictor_access_type
        spec.AutoScale = predictor_autoscale
        spec.Dataapp = create_data_app

    @property
    def spec(self) -> ModelAutobuilderSpec:
        return ModelAutobuilderSpec().copy_from(self._object.spec)

    @property
    def status(self) -> ModelAutobuilderStatus:
        self.sync()
        return ModelAutobuilderStatus().copy_from(self._object.status)

    def default(self):
        self.default_resource = True
        ModelAutobuilderSpec().apply_config(self._object.spec)

    @property
    def datasource(self) -> DataSource:
        """ Returns the Data Source associated with the resource """
        self.ensure_client_repository()
        if self.status.DataSourceName == "":
            raise ValueError("Model Autobuilder {0} has no Data Source.".format(self.name))
        return self._client.modela.DataSource(namespace=self.namespace, name=self.status.DataSourceName)

    @property
    def dataset(self) -> Dataset:
        """ Returns the Dataset associated with the resource """
        self.ensure_client_repository()
        if self.status.DatasetName == "":
            raise ValueError("Model Autobuilder {0} has no Dataset.".format(self.name))
        return self._client.modela.Dataset(namespace=self.namespace, name=self.status.DatasetName)

    @property
    def study(self) -> Study:
        """ Returns the Study associated with the resource """
        self.ensure_client_repository()
        if self.status.StudyName == "":
            raise ValueError("Model Autobuilder {0} has no Study.".format(self.name))
        return self._client.modela.Study(namespace=self.namespace, name=self.status.StudyName)

    @property
    def predictor(self) -> Predictor:
        """ Returns the Predictor associated with the resource """
        self.ensure_client_repository()
        if self.status.PredictorName == "":
            raise ValueError("Model Autobuilder {0} has no Predictor.".format(self.name))
        return self._client.modela.Predictor(namespace=self.namespace, name=self.status.PredictorName)

    @property
    def dataapp(self) -> DataApp:
        """ Returns the Data Application associated with the resource """
        self.ensure_client_repository()
        if self.status.DataSourceName == "":
            raise ValueError("Model Autobuilder {0} has no Data Application.".format(self.name))
        return self._client.modela.DataApp(namespace=self.namespace, name=self.status.PredictorName)

    def submit_and_visualize(self, replace=False, show_progress_bar=True):
        """
        Submit the resource and call visualize().

        :param replace: Replace the resource if it already exists on the cluster.
        :param show_progress_bar: If enabled, the visualization will render a progress bar indicating the study progress.
        """
        self.submit(replace)
        self.visualize(show_progress_bar)

    def visualize(self, show_progress_bar=True):
        """ Display a real-time visualization of the Study's progress

        :param show_progress_bar: If enabled, the visualization will render a progress bar.
         """
        while self.status.DatasetName == "":
            time.sleep(1 / 5)

        self.dataset.visualize()
        while self.status.StudyName == "":
            time.sleep(1 / 5)

        self.study.visualize(show_progress_bar)

    async def wait_until_phase(self, phase: ModelAutobuilderPhase):
        """ Returns a coroutine which blocks until the specified phase is reached, or the ModelAutoBuilder fails """
        while self.status.Phase not in (phase, ModelAutobuilderPhase.Failed):
            await asyncio.sleep(1 / 5)


class ModelAutobuilderClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: ModelAutobuilderServiceStub = stub

    def create(self, modelautobuilder: ModelAutobuilder) -> bool:
        request = CreateModelAutobuilderRequest()
        request.modelautobuilder.CopyFrom(modelautobuilder.raw_message)
        try:
            response = self.__stub.CreateModelAutobuilder(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, modelautobuilder: ModelAutobuilder) -> bool:
        request = UpdateModelAutobuilderRequest()
        request.modelautobuilder.CopyFrom(modelautobuilder.raw_message)
        try:
            self.__stub.UpdateModelAutobuilder(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> ModelAutobuilder:
        request = GetModelAutobuilderRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetModelAutobuilder(request)
            return ModelAutobuilder(response.modelautobuilder, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteModelAutobuilderRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteModelAutobuilder(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str, labels: dict = None) -> List[ModelAutobuilder]:
        request = ListModelAutobuildersRequest()
        request.namespace = namespace
        if labels is not None:
            request.labels.update(labels)

        try:
            response = self.__stub.ListModelAutobuilders(request)
            return [ModelAutobuilder(item, self) for item in response.modelautobuilders.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
