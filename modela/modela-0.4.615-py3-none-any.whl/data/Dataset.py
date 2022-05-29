import asyncio
import io
import json
import os.path
import random
import time

import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import Dataset as MDDataset
from github.com.metaprov.modelaapi.services.dataset.v1.dataset_pb2_grpc import DatasetServiceStub
from github.com.metaprov.modelaapi.services.dataset.v1.dataset_pb2 import CreateDatasetRequest, \
    UpdateDatasetRequest, \
    DeleteDatasetRequest, GetDatasetRequest, ListDatasetsRequest, GetDatasetProfileRequest
from tabulate import tabulate
from tqdm import tqdm, trange

from modela.Resource import Resource
from modela.ModelaException import ModelaException, ResourceNotFoundException
from typing import List, Union
import pandas

from modela.common import ObjectReference
from modela.data.common import *
from modela.data.DataSource import DataSource
from modela.data.models import SampleSettings, DatasetSpec, DatasetStatus, DatasetProfile
from modela.infra.models import Workload, NotificationSettings
from modela.infra.Lab import Lab
from modela.infra.VirtualBucket import VirtualBucket
from modela.training.Report import Report
from modela.training.common import TaskType
from modela.util import convert_size


class Dataset(Resource):
    def __init__(self, item: MDDataset = MDDataset(), client=None, namespace="", name="",
                 version=Resource.DefaultVersion,
                 lab: Union[ObjectReference, Lab, str] = "default-lab",
                 gen_datasource: bool = False,
                 target_column: str = None,
                 datasource: Union[DataSource, str] = "",
                 bucket: Union[VirtualBucket, str] = "default-minio-bucket",
                 dataframe: pandas.DataFrame = None,
                 data_file: str = None,
                 data_bytes: bytes = None,
                 workload: Workload = Workload("general-large"),
                 fast: bool = False,
                 sample: SampleSettings = SampleSettings(),
                 task_type: TaskType = None,
                 notification: NotificationSettings = None):
        """
        :param client: The Dataset client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param lab: The object reference, Lab object, or lab name under the tenant of the resource for which all
            Dataset-related workloads will be performed under.
        :param gen_datasource: If true, a Datasource resource will be created from the uploaded dataset and applied to
            the Dataset resource.
        :param target_column: If gen_datasource is enabled, then the target column of the data source must be specified.
        :param datasource: If specified as a string, the SDK will attempt to find a Data Source resource with the given name.
            If specified as a Data Source, or if one was found with the given name, it will be applied to the Dataset.
        :param bucket: The bucket which the raw dataset data will be uploaded to.
        :param dataframe: The Pandas Dataframe will be serialized and uploaded for ingestion with the Dataset resource.
        :param data_file: The file path which will be read and uploaded for ingestion with the Dataset resource.
        :param data_bytes: The raw data as bytes that will be uploaded for  ingestion with the Dataset resource.
        :param workload: The resource requirements which will be allocated for Dataset ingestion.
        :param fast: If enabled, the Dataset will skip validation, profiling, and reporting.
        :param sample: The sample settings of the dataset, which if enabled will select only a portion of the Dataset
          for further processing.
        :param task_type: The target task type in relation to the data being used.
        :param notification: The notification settings, which if enabled will forward events about this resource to a notifier.
        """
        self.default_resource = False
        self._profile = None
        super().__init__(item, client, namespace=namespace, name=name, version=version)
        if not self.default_resource:  # Ignore the rest of the constructor; datasets are immutable
            return

        spec = self.spec
        if type(lab) == Lab:
            lab = lab.reference
        elif type(lab) == str:
            lab = ObjectReference(Namespace=client.modela.tenant, Name=lab)
        spec.LabRef = lab

        if type(bucket) == VirtualBucket:
            bucket = bucket.name

        if gen_datasource:
            file_type = FlatFileType.Csv
        else:
            if type(datasource) == str:  # Fetch the data source in case we need to read the file type
                assert datasource != ""
                datasource = client.modela.DataSource(namespace=namespace, name=datasource)
                assert not datasource.default_resource

            file_type = datasource.spec.FileType

        if data_file is not None:
            with open(data_file, 'r') as f:
                data_bytes = f.read()
            data_file = os.path.basename(data_file)
        elif dataframe is not None:
            writer = io.BytesIO()
            if file_type == FlatFileType.Csv:
                df_encoded = dataframe.to_csv(index=False)
            elif file_type == FlatFileType.Parquet:
                df_encoded = dataframe.to_parquet(index=False)
            elif file_type == FlatFileType.Excel:
                dataframe.to_excel(writer)
                df_encoded = writer.getvalue()
            elif file_type == FlatFileType.Json:
                df_encoded = dataframe.to_json()
            elif file_type == FlatFileType.Feather:
                dataframe.to_feather(writer)
                df_encoded = writer.getvalue()
            else:
                raise TypeError(
                    "Pandas cannot deserialize a dataframe to the file type {0}. "
                    "Consider changing your data source file format.".format(file_type))
            data_bytes = bytes(df_encoded, encoding='utf-8')

        if data_bytes is not None:
            self.spec.Origin = client.modela.FileService.upload_file(data_file or name, data_bytes,
                                                                     client.modela.tenant,
                                                                     namespace, version, bucket, "datasets", name)

        if gen_datasource:
            datasource = client.modela.DataSource(namespace=namespace, name=name + "-source", version=version,
                                                  infer_bytes=data_bytes, target_column=target_column, task_type=task_type)
            datasource.submit(replace=True)

        self.spec.DatasourceName = datasource.name
        self.spec.Resources = workload
        self.spec.Task = task_type or TaskType.BinaryClassification
        if not task_type:
            print("WARNING: No task type was specified. Defaulting to binary classification")
        elif task_type != datasource.spec.Task:
            print("WARNING: Dataset task type does not match the task type of its Data Source (you: %s, it: %s)" %
                  (task_type.name, datasource.spec.Task.name))

        self.spec.Fast = fast
        if sample is not None:
            self.spec.Sample = sample

        if notification is not None:
            self.spec.Notification = notification

    @property
    def spec(self) -> DatasetSpec:
        return DatasetSpec().copy_from(self._object.spec).set_parent(self._object.spec)

    @property
    def status(self) -> DatasetStatus:
        self.sync()
        return DatasetStatus().copy_from(self._object.status)

    def default(self):
        self.default_resource = True
        DatasetSpec().apply_config(self._object.spec)

    @property
    def report(self) -> Report:
        """ Fetch the report associated with the Dataset """
        self.ensure_client_repository()
        if self.status.ReportName == "":
            raise ValueError("Dataset {0} has no report.".format(self.name))

        return self._client.modela.Report(namespace=self.namespace, name=self.status.ReportName)

    @property
    def phase(self) -> DatasetPhase:
        """ The phase specified by the status of the Dataset """
        return self.status.Phase

    @property
    def datasource(self) -> DataSource:
        """ Fetch the DataSource object associated with the Dataset """
        self.ensure_client_repository()
        return self._client.modela.DataSource(self.namespace, self.spec.DatasourceName)

    @property
    def test_prediction(self) -> str:
        """ Generate a default prediction payload for a model that would be created with the dataset. """
        target = self.datasource.target_column.Name
        return json.dumps(
            [{col.Name: self.status.Statistics.column(col.Name).Mean if col.Datatype == DataType.Number else col.Enum[0]
              for col in self.datasource.spec.Schema.Columns if col.Name != target}])

    def submit_and_visualize(self, replace: bool = False, show_progress_bar=True):
        """
        Submit the resource and call visualize().

        :param replace: Replace the resource if it already exists on the cluster.
        :param show_progress_bar: If enabled, the visualization will render a progress bar indicating the study progress.
        """
        self.submit(replace)
        self.visualize(show_progress_bar)

    def visualize(self, show_progress_bar=True):
        """
        Display a real-time visualization of the Dataset's progress

        :param show_progress_bar: If enabled, the visualization will render a progress bar indicating the dataset's progress.
        """
        desc, progress = tqdm(total=0, position=0, bar_format='{desc}  Time Elapsed: {elapsed}'), None
        if show_progress_bar:
            progress = tqdm(total=100, position=1, bar_format='{l_bar}{bar}',
                            desc=self.name, ncols=80, initial=0)

        current_status = self.status
        try:
            while True:
                if current_status == self.status:
                    time.sleep(0.1)
                    continue

                current_status = self.status
                desc.set_description_str('Phase: %s | File Size: %s | Rows: %s | Columns: %s' %
                                         (self.phase.name, convert_size(self.status.Statistics.FileSize),
                                          "[Processing]" if self.status.Statistics.Rows == 0 else self.status.Statistics.Rows,
                                          "[Processing]" if len(self.status.Statistics.Columns) == 0 else len(
                                              self.status.Statistics.Columns)))

                if self.phase in (DatasetPhase.Ready, DatasetPhase.Aborted, DatasetPhase.Failed):
                    if self.phase == DatasetPhase.Ready:
                        print("\n\n" + self.profile)
                    else:
                        if progress:
                            progress.colour = "red"
                            progress.refresh()
                        print("\nDataset was failed or aborted: %s" % current_status.FailureMessage)

                    break

                if progress:
                    progress.n = self.status.Progress
                    progress.last_print_n = self.status.Progress
                    progress.refresh()

        except KeyboardInterrupt:
            pass

        desc.close()
        if progress:
            progress.close()

    @property
    def profile(self) -> str:
        """
        Returns an ASCII-rendered table of the Dataset's profile
        """
        profile = self.get_profile()

        table = []
        for col in profile.Columns:
            table.append([col.Name, col.Type, col.Distinct, col.Missing,
                          '{0:.3g}'.format(col.Mean), '{0:.3g}'.format(col.Stddev), col.P50, col.Min, col.Max,
                          '{0:.3g}'.format(col.CorrToTarget), '{0:.3g}'.format(col.Variance),
                          '{0:.3g}'.format(col.Skewness), '{0:.3g}'.format(col.Kurtosis)])

        table = tabulate(table, tablefmt='pretty', headers=['Column', 'Data Type', 'Distinct', 'Missing', 'Mean',
                                                            'Stddev', 'Median', 'Min', 'Max', 'Corr. To Target',
                                                            'Variance', 'Skewness', 'Kurtosis'])
        return table + "\n"
        # TODO: jupyter support, print all viz plots in jupyter

    @property
    def details(self) -> str:
        """
        Returns an ASCII-rendered table of the Dataset's statistics
        """
        table = []
        for col in self.status.Statistics.Columns:
            table.append([col.Name, col.Datatype.name, col.Distinct, col.Missing,
                          '{0:.3g}'.format(col.Mean), '{0:.3g}'.format(col.Stddev), col.P50, col.Min, col.Max,
                          '{0:.3g}'.format(col.Skewness), '{0:.3g}'.format(col.Kurtosis)])

        table = tabulate(table, tablefmt='pretty', headers=['Column', 'Data Type', 'Distinct', 'Missing', 'Mean',
                                                            'Stddev', 'Median', 'Min', 'Max', 'Skewness', 'Kurtosis'])
        return table + "\n"

    def get_profile(self) -> DatasetProfile:
        if self._profile:
            return self._profile
        if hasattr(self, "_client"):
            self._profile = self._client.profile(self.namespace, self.name)
            return self._profile
        else:
            raise AttributeError("Object has no client repository")

    async def wait_until_phase(self, phase: DatasetPhase):
        """ Returns a coroutine which blocks until the specified phase is reached, or the Dataset fails """
        while self.status.Phase not in (phase, DatasetPhase.Failed):
            await asyncio.sleep(1/5)

    def __repr__(self):
        out = super().__repr__()
        if len(self.status.Statistics.Columns) > 0:
            out += "\n" + self.details

        return out


class DatasetClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: DatasetServiceStub = stub

    def create(self, dataset: Dataset) -> bool:
        request = CreateDatasetRequest()
        request.dataset.CopyFrom(dataset.raw_message)
        try:
            response = self.__stub.CreateDataset(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, dataset: Dataset) -> bool:
        request = UpdateDatasetRequest()
        request.dataset.CopyFrom(dataset.raw_message)
        try:
            self.__stub.UpdateDataset(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Dataset:
        request = GetDatasetRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetDataset(request)
            return Dataset(response.dataset, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteDatasetRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteDataset(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> List[Dataset]:
        request = ListDatasetsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListDatasets(request)
            return [Dataset(item, self) for item in response.datasets.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)

    def profile(self, namespace: str, name: str) -> DatasetProfile:
        request = GetDatasetProfileRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetDatasetProfile(request)
            return DatasetProfile().copy_from(response.profile)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False
