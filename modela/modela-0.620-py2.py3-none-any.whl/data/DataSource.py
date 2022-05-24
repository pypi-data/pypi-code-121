import os

import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import DataSource as MDDataSource
from github.com.metaprov.modelaapi.services.datasource.v1.datasource_pb2_grpc import DataSourceServiceStub
from github.com.metaprov.modelaapi.services.datasource.v1.datasource_pb2 import CreateDataSourceRequest, \
    UpdateDataSourceRequest, \
    DeleteDataSourceRequest, GetDataSourceRequest, ListDataSourceRequest, InferSchemaRequest

from modela.data.common import *
from modela.data.models import ExcelNotebookFormat, CsvFileFormat, Column, DataType, DataSourceSpec, ColumnProfile, \
    DataLocation
from modela.Resource import *
from modela.ModelaException import ModelaException
from typing import List, Union
import pandas
from modela.training.common import *


class DataSource(Resource):
    def __init__(self, item: MDDataSource = MDDataSource(), client=None, namespace="", name="",
                 version=Resource.DefaultVersion,
                 bucket: str = "default-minio-bucket",
                 infer_file: str = None,
                 infer_dataframe: pandas.DataFrame = None,
                 infer_bytes: bytes = None,
                 target_column: str = "",
                 file_type: FlatFileType = None,
                 task_type: TaskType = None,
                 csv_config: CsvFileFormat = None,
                 excel_config: ExcelNotebookFormat = None):
        """
        :param client: The Data Source client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param version: The version of the resource.
        :param bucket: If data is provided for inference then a bucket must be provided.
        :param infer_file: If specified, the SDK will attempt read a file with the given path and will upload it to
            analyse the columns and generate a schema that will be applied to the resource.
        :param infer_dataframe: If specified, the Pandas DataFrame will be serialized and uploaded to analyse
            the columns and generate a schema that will be applied to the resource.
        :param infer_bytes: If specified, the raw byte data will be uploaded to analyse
            the columns and generate a schema that will be applied to the resource.
        :param target_column: The name of the target column used when training a model. This parameter only has effect
            when data is uploaded to infer a schema.
        :param file_type: The file type of raw data, used when ingesting a Dataset from a file, or creating a data snapshot
            from a database source. If inferring from a dataframe, the file type will default to CSV.
        :param task_type: The target task type in relation to the data being used.
        :param csv_config: The CSV file format of the raw data.
        :param excel_config: The Excel file format of the raw data.
        """
        self.default_resource = False
        super().__init__(item, client, namespace=namespace, name=name, version=version)

        if infer_file is not None:
            with open(infer_file, 'rb') as f:
                infer_bytes = f.read()
            infer_file = os.path.basename(infer_file)
        elif infer_dataframe is not None:
            file_type = FlatFileType.Csv
            infer_bytes = infer_dataframe.to_csv(index=False)
        if infer_bytes is not None:
            infer_location = client.modela.FileService.upload_file(infer_file or name, infer_bytes, client.modela.tenant,
                                                                   namespace, version, bucket, "datasources", name)

            profile = client.infer(namespace, infer_location, data_source=self, version=version)
            schema_columns = self.spec.Schema.Columns
            del schema_columns[:]
            for column in profile:
                col = Column()
                col.Datatype = DataType(column.Type)
                col.Name = column.Name
                col.Enum = column.Values
                if target_column == col.Name:
                    col.Target = True
                    target_column = None

                schema_columns.append(col)

            if target_column != None:
                print("WARNING: The target column {0} was not found in the dataset during schema inference.".format(target_column))


        if file_type is not None:
            self.spec.FileType = file_type
            if not self.default_resource:
                print("WARNING: Changing the file type of an existing Data Source is not recommended. "
                      "Create a new Data Source resource if necessary.")
        elif self.default_resource:
            print("WARNING: Data Source was created without a file type. Defaulting to FlatFileType.Csv")
            self.spec.FileType = FlatFileType.Csv

        if task_type is not None:
            self.spec.Task = task_type
            if not self.default_resource:
                print("WARNING: Changing the task type of an existing Data Source is not recommended. "
                      "Create a new Data Source resource if necessary.")
        elif self.default_resource:
            print("WARNING: Data Source was created without a task type. Defaulting to TaskType.BinaryClassification")
            self.spec.Task = TaskType.BinaryClassification

        if csv_config is not None:
            self.spec.Csvfile = csv_config

        if excel_config is not None:
            self.spec.ExcelNotebook = excel_config

    @property
    def spec(self) -> DataSourceSpec:
        return DataSourceSpec().copy_from(self._object.spec).set_parent(self._object.spec)

    @property
    def schema(self):
        return self.spec.Schema

    @property
    def target_column(self) -> Column:
        """ Get the target column specified by the schema """
        return [col for col in self.schema.Columns if col.Target][0]

    def column(self, name: str) -> Column:
        """ Get the column with the specified name from the schema """
        search = [col for col in self.schema.Columns if col.Name == name]
        if len(search) == 0:
            raise ValueError("Data source {0} does not have a column named {1}".format(self.name, name))

        return search[0]

    def __getitem__(self, col) -> Column:
        """ Get the column with the specified name from the schema """
        return self.column(col)

    def default(self):
        self.default_resource = True
        DataSourceSpec().apply_config(self._object.spec)


class DataSourceClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: DataSourceServiceStub = stub

    def create(self, datasource: DataSource) -> bool:
        request = CreateDataSourceRequest()
        request.datasource.CopyFrom(datasource.raw_message)
        try:
            response = self.__stub.CreateDataSource(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, datasource: DataSource) -> bool:
        request = UpdateDataSourceRequest()
        request.datasource.CopyFrom(datasource.raw_message)
        try:
            self.__stub.UpdateDataSource(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[DataSource, bool]:
        request = GetDataSourceRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetDataSource(request)
            return DataSource(response.datasource, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteDataSourceRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteDataSource(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[DataSource], bool]:
        request = ListDataSourceRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListDataSources(request)
            return [DataSource(item, self) for item in response.datasources.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def infer(self, namespace: str, location: DataLocation, file_type: FlatFileType = FlatFileType.Csv,
              data_source: DataSource = None, version=Resource.DefaultVersion) -> List[ColumnProfile]:
        request = InferSchemaRequest()
        request.namespace = namespace
        (data_source.spec if data_source else DataSourceSpec()).apply_config(request.datasource.spec)
        request.datasource.spec.versionName = version
        request.datasource.spec.fileType = file_type.value
        request.location.CopyFrom(location.to_message())

        try:
            response = self.__stub.InferSchema(request)
            return [ColumnProfile().copy_from(item) for item in response.columns]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False
