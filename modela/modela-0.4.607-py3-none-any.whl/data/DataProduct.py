import grpc
from github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 import DataProduct as MDDataProduct
from github.com.metaprov.modelaapi.services.dataproduct.v1.dataproduct_pb2_grpc import DataProductServiceStub
from github.com.metaprov.modelaapi.services.dataproduct.v1.dataproduct_pb2 import CreateDataProductRequest, \
    UpdateDataProductRequest, \
    DeleteDataProductRequest, GetDataProductRequest, ListDataProductsRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from typing import List, Union

from modela.infra.VirtualBucket import VirtualBucket
from modela.infra.ServingSite import ServingSite
from modela.infra.Lab import Lab
import modela.data.models
from modela.data.models import DataProductSpec, Permissions, DataLocation
from modela.infra.models import NotificationSettings, Workload
from modela.training.common import TaskType


class DataProduct(Resource):
    def __init__(self, item: MDDataProduct = MDDataProduct(), client=None, namespace="", name="",
                 serving_site: Union[ServingSite, str] = None,
                 lab: Union[Lab, str] = None,
                 public: bool = None,
                 task_type: TaskType = None,
                 default_training_workload: Workload = None,
                 default_serving_workload: Workload = None,
                 default_bucket: Union[VirtualBucket, str] = None,
                 notification_settings: NotificationSettings = None,
                 permissions: Permissions = None):
        """
        :param client: The Data Product client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param serving_site: The default Serving Site of the Data Product.
        :param lab: The default Lab of the Data Product.
        :param public: If enabled, the Data Product will be publicly accessible by all users without permissions.
        :param task_type: The default task type for child resources of the Data Product.
        :param default_training_workload: The default workload for training Jobs under the Data Product
        :param default_serving_workload: The default workload for model serving Jobs under the Data Product.
        :param default_bucket: The default bucket used for child resources of the Data Product.
        :param notification_settings: The default notification settings used for child resources of the Data Product.
        :param permissions: The permission specification that dictates which users can access the resources under
          the Data Product and what actions they can perform.
        """
        super().__init__(item, client, namespace=namespace, name=name)

        spec = self.spec
        if type(serving_site) == ServingSite:
            serving_site = serving_site.name
        spec.ServingSiteName = serving_site

        if type(lab) == Lab:
            lab = lab.name
        spec.LabName = lab

        if spec.Public is not None:
            spec.Public = public

        if task_type is not None:
            spec.Task = task_type

        if default_training_workload is not None:
            spec.TrainingResources = default_training_workload

        if default_serving_workload is not None:
            spec.ServingResources = default_serving_workload

        if default_bucket is not None:
            spec.DataLocation = DataLocation(BucketName=default_bucket)

        if notification_settings is not None:
            spec.Notification = notification_settings

        if permissions is not None:
            spec.Permissions = permissions

    @property
    def spec(self) -> DataProductSpec:
        return DataProductSpec().copy_from(self._object.spec).set_parent(self._object.spec)

    def default(self):
        DataProductSpec().apply_config(self._object.spec)


class DataProductClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: DataProductServiceStub = stub

    def create(self, dataproduct: DataProduct) -> bool:
        request = CreateDataProductRequest()
        request.dataproduct.CopyFrom(dataproduct.raw_message)
        try:
            response = self.__stub.CreateDataProduct(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, dataproduct: DataProduct) -> bool:
        request = UpdateDataProductRequest()
        request.dataproduct.CopyFrom(dataproduct.raw_message)
        try:
            self.__stub.UpdateDataProduct(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[DataProduct, bool]:
        request = GetDataProductRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetDataProduct(request)
            return DataProduct(response.dataproduct, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteDataProductRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteDataProduct(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[DataProduct], bool]:
        request = ListDataProductsRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListDataProducts(request)
            return [DataProduct(item, self) for item in response.dataproducts.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False


